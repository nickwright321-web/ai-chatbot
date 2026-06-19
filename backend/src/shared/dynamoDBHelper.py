
import boto3,time

from chat_processor.ChatMessage import ChatMessage

dynamodb = boto3.resource("dynamodb")
chat_table = dynamodb.Table("ChatHistory")

################################
#Chat History functions
################################
    
def saveChatMessage(connectionId: str, role: str, message: ChatMessage):
    
    chat_table.put_item(
        Item={
            "connectionId": connectionId,
            "timestamp": int(time.time() * 1000),
            "role": role,
            "message": message.text,
            "intent":message.intent
        }
    )
    
def getChatHistory(connection_id: str, limit: int = 10):
    resp = chat_table.query(
        KeyConditionExpression="connectionId = :c",
        ExpressionAttributeValues={":c": connection_id},
        ScanIndexForward=False,  # newest first
        Limit=limit + 1          # fetch one extra in case -1 is present
    )

    items = resp.get("Items", [])

    # Remove the session-state row (timestamp = -1)
    items = [item for item in items if item.get("timestamp") != -1]

    # Reverse so oldest → newest
    return list(reversed(items[:limit]))


################################
# Session State functions
################################

def loadSessionState(connectionId):
    resp = chat_table.get_item(
        Key={
            "connectionId": connectionId,
            "timestamp": -1
        }
    )
    return resp.get("Item")


def saveSessionState(connectionId, pending_intent):
    chat_table.put_item(
        Item={
            "connectionId": connectionId,
            "timestamp": -1,
            "pending_intent": pending_intent,
            "lastUpdated": int(time.time())
        }
    )


def clearSessionState(connectionId):
    chat_table.delete_item(
        Key={
            "connectionId": connectionId,
            "timestamp": -1
        }
    )