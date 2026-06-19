import os
import json
import boto3
import logging

from datetime import datetime
from chat_processor.ChatMessage import ChatMessage
from chat_processor.ai_engine.factory import create_engine
from shared.dynamoDBHelper import saveChatMessage,getChatHistory,loadSessionState,saveSessionState
from chat_processor.SQSHelper import sendToInboundQueue

# 1. Initialize AWS S3 client and Tokenizer
s3_client = boto3.client('s3')

# get the inbound queue name for forwarding messages
QUEUE_NAME = os.environ.get("INBOUND_MESSAGES_QUEUE_URL", "InboundMessages")

#Plugin architecture to allow alternative models
ENGINE_ID = os.environ.get("ENGINE_ID", "Mistral7b2")
BOB_PROMPT = os.environ.get("BOB_PROMPT", "s3://bob-training-data-132696833143-eu-west-2/bob-prompt.txt")

def get_engine():
    return create_engine(ENGINE_ID)

AI_NAME = os.environ.get("AI_NAME", "Bob")

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

class Gateway:
    _client = None

    @classmethod
    def init(cls, client):
        cls._client = client

    @classmethod
    def get(cls):
        if cls._client is None:
            raise RuntimeError("Gateway client not initialised")
        return cls._client

def lambda_handler(event, context, apigw_client_factory=get_apigw_client):

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

        logger.info("DOMAIN: %s", domain)
        logger.info("STAGE: %s", stage)

        try:
            logger.info("Getting API Gateway...")
            apigw = apigw_client_factory(domain, stage)
            Gateway.init(apigw)

            logger.info("API Gateway retrieved successfully")

        except Exception as e:
            logger.error(f"Failed to get API Gateway: {e}")

        #start processing the message
        try:

            pending_intent = checkPendingIntent(connectionId, message)

            if pending_intent == "QUEUE":
                # forward to queue
                sendToInboundQueue(connectionId, companyId, message, QUEUE_NAME)

                aiMessage = "OK, I'll forward your call to someone who can help!"

                postToClient(AI_NAME, aiMessage, connectionId)

                return {
                        "statusCode": 200, 
                        "body": f"Message received and forwarded to {QUEUE_NAME}"
                        }
            
            logger.info(f"Retrieving chat history for {connectionId}")
            chatHistory = getChatHistory(connectionId, 10)
            logger.info(f"Retrieved chat history for {connectionId}")

            #Save the current message after retrieving chat history, to avoid
            # duplication 
            # 
            logger.info(f"Saving message for {connectionId}...")           
            saveChatMessage(connectionId, "User", ChatMessage(text=message, intent="user"))
            logger.info(f"Message saved successfully for {connectionId}...")

            #Send the user's message and chat history to the AI

            ai_reply:ChatMessage = get_engine().sendToAI(message,chatHistory)
            
            # save the AI response with the intent
            logger.info(f"Saving AI response for {connectionId}...")  
            saveChatMessage(connectionId, AI_NAME, ai_reply)
            logger.info(f"AI response saved successfully for {connectionId}...")

            savePendingIntent(connectionId,ai_reply.intent)

            # post the AI reply back to the client via the 
            # websocket    
            postToClient(AI_NAME, ai_reply.text, connectionId)

        except Exception as e:
            logger.error("Sending message to client6:%s", e)
           # print("ERROR: Sending message to client:", e)

        return {"statusCode": 200, "body": "Message received"}


    except Exception as e:
        logger.error("Error processing event:%s", e)        
       # print(f"Error processing event: {e}")
        return {"statusCode": 400, "body": "Invalid event format"}

def postToClient(agentName:str, message:str, connectionId:str):
    apigw = Gateway.get()
    reply:dict[str,str] = {   "agentName": agentName,
                    "message": message
            }

    apigw.post_to_connection(
        ConnectionId=connectionId,
        Data=json.dumps(reply).encode("utf-8")
    )
    logger.info("Message sent OK")

def checkPendingIntent(connectionId:str, message:str):
    # Check for pending intent
    state = loadSessionState(connectionId)
    pending_intent = state.get("pending_intent") if state else None

    if pending_intent:
        lower = message.lower()

        if lower in ["yes", "y", "ok", "sure"]:
            #  forward_to_queue(pending_intent, connectionId)
            #  clearSessionState(connectionId)
            #  postToClient(AI_NAME, "Okay, forwarding you now.", connectionId)
            #  return {"statusCode": 200}
            return "QUEUE"

        if lower in ["no", "n"]:
            return "CONTINUE"
            #  postToClient(AI_NAME, "No problem, how else can I help?", connectionId)
            #  return {"statusCode": 200}

    # postToClient(AI_NAME, "Just to confirm, would you like me to forward you.", connectionId)
    #  return {"statusCode": 200}

def savePendingIntent(connectionId:str, intent:str):
    # store a pending intent
    if intent in ("SALES", "TECH_SUPPORT"):
        saveSessionState(connectionId, intent)   