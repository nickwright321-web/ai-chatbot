import os
import json
import boto3

# Connection lifecycle handler for WebSocket API
# Handles $connect and $disconnect events to manage active connections in DynamoDB
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["CONNECTIONS_TABLE_NAME"])

def lambda_handler(event, context):

    print(f"Received event: {json.dumps(event)}")

    route = event["requestContext"]["routeKey"]
    connection_id = event["requestContext"]["connectionId"]

    print(f"Received {route} event for connection ID: {connection_id}")

    if route == "$connect":
        table.put_item(Item={"connectionId": connection_id})

    elif route == "$disconnect":
        table.delete_item(Key={"connectionId": connection_id})

    return {"statusCode": 200}
