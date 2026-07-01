import os
import json
import boto3
import logging

from datetime import datetime
from chat_processor.ChatMessage import ChatMessage
from chat_processor.ai_engine.factory import create_engine
from shared.sessionHelper import loadSessionState,saveSessionState,clearSessionState
from shared.chatHistoryHelper import saveChatMessage,getChatHistory
from shared.SQSHelper import sendToInboundQueue
from shared.Gateway import Gateway
from shared.intentHelper import getUserConf

# 1. Initialize AWS S3 client and Tokenizer
s3_client = boto3.client('s3')

#Plugin architecture to allow alternative models
ENGINE_ID = os.environ.get("ENGINE_ID", "Mistral7b2")
BOB_PROMPT = os.environ.get("BOB_PROMPT", "s3://bob-training-data-132696833143-eu-west-2/bob-prompt.txt")
AI_NAME = os.environ.get("AI_NAME", "Bob")

def get_engine():
    return create_engine(ENGINE_ID)


#initialise the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# for debugging, we need to inject a mock
# API Gateway passed from the test script.
# If no instance is passed, then this is
# a Lambda call from AWS so return the
# botob3 client

def get_apigw_client(domain, stage):
    return boto3.client(
        "apigatewaymanagementapi",
        endpoint_url=f"https://{domain}/{stage}"
    )

def lambda_handler(event, context, apigw_client_factory=get_apigw_client):
    #inject the gateway client so it can be mocked when testing

    try:
       
        event_msg = f"EVENT: {json.dumps(event)}"
        # print(event_msg)
        logger.info(event_msg)

        route = event["requestContext"].get("routeKey")
        connectionId = event["requestContext"].get("connectionId")
        companyId = event["requestContext"]["authorizer"].get("companyId", "DemoComp")

        body = json.loads(event.get("body", "{}"))
        message = body.get("message", "")

        logger.info(f"Received {route} event for connection ID: {connectionId}")
        logger.info(f"Message: {message}")

        # Create API Gateway Management API client
        domain = event["requestContext"]["domainName"]
        stage = event["requestContext"]["stage"]

        try:
            logger.info("Getting API Gateway...")
            apigw = apigw_client_factory(domain, stage)
            Gateway.init(apigw)

            logger.info("API Gateway retrieved successfully")

        except Exception as e:
            logger.error(f"Failed to get API Gateway: {e}")

        #start processing the message
        try:

            # check for an existing intent. If the user is confirming
            # an intent, we should just forward to the CCForwarder
            # and ignore.
            state = loadSessionState(connectionId)
            pending_intent = state.get("pending_intent") if state else None

            if pending_intent:
                
                logger.info(f"User is replying to a confirmation prompt: {message}, pending intent {pending_intent}")

                userConf = getUserConf(message.lower())                
                
                if userConf=="YES":
                    Gateway.post(AI_NAME, f"OK, I'll forward you now...", connectionId)
                    sendToInboundQueue(
                        connectionId=connectionId,
                        companyId=companyId,
                        intent=pending_intent,
                        userMessage=message,
                        domain=domain,
                        stage=stage
                    )
                    return {"statusCode": 200}
                
                elif userConf == "NO":
                    clearSessionState(connectionId)
                    Gateway.post(AI_NAME, "No problem, how else can I help?", connectionId)
                    return {"statusCode": 200}
                else:
                    Gateway.post(AI_NAME, "Just to confirm — would you like me to forward you?", connectionId)
                    return {"statusCode": 200}

            logger.info(f"Retrieving chat history for {connectionId}")
            chatHistory = getChatHistory(connectionId, 10)
            logger.info(f"Retrieved chat history for {connectionId}")

            #Save the current message after retrieving chat history, to avoid
            # duplication 
            logger.info(f"Saving message for {connectionId}...")           
            saveChatMessage(connectionId, "User", ChatMessage(text=message, intent="user"))
            logger.info(f"Message saved successfully for {connectionId}...")

            #Send the user's message and chat history to the AI
            ai_reply:ChatMessage = get_engine().sendToAI(message,chatHistory)
            
            #save the pending intent            
            if ai_reply.intent in ("SALES", "TECH_SUPPORT"):
                saveSessionState(connectionId, ai_reply.intent)

            #send message to the inbound queue
            sendToInboundQueue(
                connectionId=connectionId,
                companyId=companyId,
                intent=ai_reply.intent,
                userMessage=message,
                domain = domain,
                stage = stage
            )

            
            # save the AI response with the intent
            logger.info(f"Saving AI response for {connectionId}...")  
            saveChatMessage(connectionId, AI_NAME, ai_reply)
            logger.info(f"AI response saved successfully for {connectionId}...")

            logger.info(f"AI Response to user: {ai_reply.text}")
            #postToClient(AI_NAME, ai_reply.text, connectionId)
            Gateway.post(AI_NAME, ai_reply.text, connectionId)
            

        except Exception as e:
            logger.error("Error Sending message to client:%s", e)
           # print("ERROR: Sending message to client:", e)

        return {"statusCode": 200, "body": "Message received"}


    except Exception as e:
        logger.error("Error processing event:%s", e)        
       # print(f"Error processing event: {e}")
        return {"statusCode": 400, "body": "Invalid event format"}

# def postToClient(agentName:str, message:str, connectionId:str):
#     apigw = Gateway.get()
#     reply:dict[str,str] = {   "agentName": agentName,
#                     "message": message
#             }

#     apigw.post_to_connection(
#         ConnectionId=connectionId,
#         Data=json.dumps(reply).encode("utf-8")
#     )
#     logger.info("Message sent OK")

def savePendingIntent(connectionId:str, intent:str):
    # store a pending intent
    if intent in ("SALES", "TECH_SUPPORT"):
        saveSessionState(connectionId, intent)   