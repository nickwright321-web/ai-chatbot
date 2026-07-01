import os
import json
import time
from shared.ConnectionsRepository import ConnectionsRepository
from shared.logger import LogInfo, LogWarning, LogError
from shared.sessionHelper import clearSessionState

# Connection lifecycle handler for WebSocket API
# Handles $connect and $disconnect events to manage active connections in DynamoDB

def lambda_handler(event, context):

    event_str = json.dumps(event)
    print(f"Received event: {event_str}")

    connRepo = ConnectionsRepository()

    try:

        request_context = event.get("requestContext") or {}
        route = request_context.get("routeKey")
        connectionId = request_context.get("connectionId")

        print(f"Received {route} event for connection ID: {connectionId}")

        if route == "$connect":
            domainName = request_context.get("domainName")
            stage =  request_context.get("stage")
            connRepo.put_connection(connectionId,domainName,stage)

        elif route == "$disconnect":
            connRepo.delete_connection(connectionId)
            clearSessionState(connectionId)

        return {"statusCode": 200}
    
    except Exception as e:
        LogError(f"ERROR: {e}")