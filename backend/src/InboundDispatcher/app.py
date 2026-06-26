import json,logging
from shared.chatHistoryHelper import getChatHistory
from InboundDispatcher.cc_adapters.cc_factory import getAdapter
from InboundDispatcher.cc_adapters import ccAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    #forwards a queued message to the cc platform
    
    # Triggered by the CC Forwarder queue

    event_msg = f"EVENT: {json.dumps(event)}"
    logger.info(event_msg)

    records = event["Records"]

    for record in records:
        body = json.loads(record["body"])
        logger.info(f"Processing inbound message: {body}")

        connectionId = body.get("connectionId") 
        companyId = body.get("companyId")         

        logger.info(f"Getting Chat History for: {connectionId}")
        #get the chat history and format it for
        #forwarding to the CC
        chatHistory = getChatHistory(connectionId)

        #now get the cc adapter so you can 
        #send the message to the CC

        adapter:ccAdapter = getAdapter(companyId)

        adapter.send_message(messages = chatHistory)


    return {"statusCode": 200, "body": "success"}

