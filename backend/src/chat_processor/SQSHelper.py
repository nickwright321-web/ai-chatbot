import boto3,json
from datetime import datetime

sqs = boto3.client("sqs")
   
def sendToInboundQueue(connection_id: str, companyId: str, user_message: str, queueName: str):
    
    payload = {
        "connectionId": connection_id,
        "companyId": companyId,
        "userMessage": user_message,
        "timestamp": datetime.utcnow().isoformat()
    }

    queueUrl = getQueueUrl(queueName)

    sqs.send_message(
        QueueUrl=queueUrl,
        MessageBody=json.dumps(payload)
    )


def getQueueUrl(queue_name: str) -> str:
    response = sqs.get_queue_url(QueueName=queue_name)
    return response["QueueUrl"]