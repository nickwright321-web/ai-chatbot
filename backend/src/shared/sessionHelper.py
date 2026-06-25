
import boto3,time

from chat_processor.ChatMessage import ChatMessage

dynamodb = boto3.resource("dynamodb")
chat_sessions_table = dynamodb.Table("ChatSessions")


################################
# Session State functions
################################

def loadSessionState(connectionId):
    resp = chat_sessions_table.get_item(
        Key={
            "connectionId": connectionId,
            "sortKey": "STATE"
        }
    )
    return resp.get("Item")



def saveSessionState(connectionId, pending_intent):
    chat_sessions_table.put_item(
        Item={
            "connectionId": connectionId,
            "sortKey": "STATE",
            "pending_intent": pending_intent,
            "lastUpdated": int(time.time())
        }
    )


def clearSessionState(connectionId):
    chat_sessions_table.delete_item(
        Key={
            "connectionId": connectionId,
            "sortKey": "STATE"
        }
    )
