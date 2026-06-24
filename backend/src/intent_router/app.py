import json
import logging
import boto3

from shared.dynamoDBHelper import loadSessionState, saveSessionState, clearSessionState
from shared.SQSHelper import sendToCCForwarderQueue
from shared.Gateway import Gateway

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ROUTABLE_INTENTS = {"SALES", "TECH_SUPPORT", "GENERAL ENQUIRY"}

def lambda_handler(event, context):
    # Triggered by the Intent queue
    event_msg = f"EVENT: {json.dumps(event)}"
    # print(event_msg)
    logger.info(event_msg)

    records = event["Records"]

    for record in records:
        body = json.loads(record["body"])
        logger.info(f"Processing inbound message: {body}")

        connectionId = body.get("connectionId")
        companyId = body.get("companyId")
        userMessage = body.get("userMessage")
        intent = body.get("intent")
        domain = body.get("wsDomain")
        stage = body.get("wsStage")

        logger.info(f"Message: {userMessage}")

        #create the apigateway for sending confirmation
        #prompt back to user
        logging.info("Getting websocket Gateway...")
        Gateway.init(get_apigw_client(domain,stage))
        logging.info("Web socket API created successfully")

        # 1. Check if user is confirming a pending intent
        state = loadSessionState(connectionId)
        pending_intent = state.get("pending_intent") if state else None

        if pending_intent:
            logger.info(f"Pending intent found: {pending_intent}")

            user_reply = userMessage.lower()

            if user_reply in ["yes", "y", "ok", "sure"]:
                logger.info("User confirmed intent. Forwarding to CC.")
                clearSessionState(connectionId)

                sendToCCForwarderQueue(
                    connectionId=connectionId,
                    companyId=companyId,
                    userMessage=userMessage,
                    intent=pending_intent
                )
                continue

            if user_reply in ["no", "n"]:
                logger.info("User declined intent. Clearing pending state.")
                clearSessionState(connectionId)
                continue

            # If user said something else, ignore and wait for yes/no
            logger.info("User responded but not yes/no. Waiting.")
            continue

        # 2. No pending intent — check if AI detected a new intent
        if intent in ROUTABLE_INTENTS:
            logger.info(f"Detected intent requiring confirmation: {intent}")

            # Save pending intent
            saveSessionState(connectionId, intent)

            # Ask user for confirmation (via ChatProcessor)
            
            sendConfirmationPrompt(connectionId, intent)
            continue

        # 3. No routing needed — ignore
        logger.info("No routing required for this message.")

    return {"statusCode": 200}


def get_apigw_client(domain, stage):
    return boto3.client(
        "apigatewaymanagementapi",
        endpoint_url=f"https://{domain}/{stage}"
    )

def sendConfirmationPrompt(connectionId, intent):
    
    #if the user doesn't confirm, prompt them for a reply
    apigw = Gateway.get()

    prompt = f"Just to confirm, would you like me to forward you to {intent.replace('_', ' ').title()}?"
    
    logger.info(f"AI Response to user: {prompt}")

    apigw.post_to_connection(
        ConnectionId=connectionId,
        Data=json.dumps({
            "agentName": "Bob",
            "message": prompt
        }).encode("utf-8")
    )

    logger.info("Confirmation prompt sent.")