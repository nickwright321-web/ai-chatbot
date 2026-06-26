import boto3,json,os
from datetime import datetime, timezone
import warnings
from functools import wraps

warnings.simplefilter("always", DeprecationWarning)


sqs = boto3.client("sqs")

QUEUE_NAME = os.environ.get("QUEUE_NAME", "")

def deprecated(reason: str = ""):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"Function {func.__name__} is deprecated. {reason}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@deprecated("Use sendToQueue instead.")
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


@deprecated("Use sendToQueue instead.")
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

def sendToQueue(payload:str):
        sqs.send_message(
        QueueUrl=QUEUE_NAME,
        MessageBody=json.dumps(payload)
    )
    
