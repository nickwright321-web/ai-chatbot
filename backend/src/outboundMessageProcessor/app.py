import logging,json
from datetime import datetime, timezone
from shared.SQSHelper import sendToQueue

#initialise the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    try:
        event_json = json.dumps(event, separators=(",", ":"))
        logger.info(f"EVENT: {event_json}")
            
        if (body_str := event.get("body")) is None:
            raise Exception("Missing Body")

        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            raise Exception("Body is not valid JSON")

        if(message := body.get("message")) is None:
            raise Exception("No message received")
        
        if(connectionId := message.get("connectionId")) is None:
            raise Exception("No connection ID received")
    
    except Exception as e:
        logger.error(
                f"ERROR: Delivery failed: {e}",
                exc_info=True
            )
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid message: {e}"})}
    
    try:
        
        logger.info(f"Sending Message: {message} for connectionId {connectionId}")
        #send the message to the outbound message queue
        sendToQueue({
                "connectionId": connectionId,
                "message": message,
                "timestamp":datetime.now(timezone.utc).isoformat()
            } )
    except Exception as e:
        logger.error(
                f"ERROR: Delivery failed: {e}",
                exc_info=True
            )
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to send the message to a queue: {e}"})}
    
    return {"statusCode": 200, "body": "Message received"}  