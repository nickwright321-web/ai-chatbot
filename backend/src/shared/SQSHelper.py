import boto3,json,os
from datetime import datetime, timezone

sqs = boto3.client("sqs")

QUEUE_NAME = os.environ.get("QUEUE_NAME", "")

def sendToInboundQueue(connectionId: str, companyId: str, intent:str, userMessage: str, domain: str, stage: str):
    
    payload = {
        "connectionId": connectionId,
        "companyId": companyId,
        "userMessage": userMessage,
        "intent": intent,
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "wsDomain": domain,
        "wsStage": stage
    }

    sqs.send_message(
        QueueUrl=QUEUE_NAME,
        MessageBody=json.dumps(payload)
    )

def sendToCCForwarderQueue(connectionId: str, companyId: str, intent: str, userMessage: str):
    payload = {
        "connectionId": connectionId,
        "companyId": companyId,
        "userMessage": userMessage,
        "intent": intent,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    sqs.send_message(
        QueueUrl=QUEUE_NAME,
        MessageBody=json.dumps(payload)
    )
    
                   