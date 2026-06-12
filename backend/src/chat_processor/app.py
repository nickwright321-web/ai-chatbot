import os
import json
import boto3


def lambda_handler(event, context):

    try:
        print(f"Received event: {json.dumps(event)}")

        route = event["requestContext"]["routeKey"]
        connection_id = event["requestContext"]["connectionId"]

        body = json.loads(event.get("body", "{}"))
        message = body.get("message", "")

        print(f"Received {route} event for connection ID: {connection_id}")
        print(f"Message: {message}")

        # Create API Gateway Management API client
        domain = event["requestContext"]["domainName"]
        stage = event["requestContext"]["stage"]

        print("DOMAIN:", domain)
        print("STAGE:", stage)
        print("CALLBACK URL:", f"https://{domain}/{stage}")

        apigw = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=f"https://{domain}/{stage}"
        )

        # Send a message back to the client
        try:
            apigw.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps({"echo": message}).encode("utf-8")
            )
            print("Message sent OK")
        except Exception as e:
            print("Error sending message:", e)


        return {"statusCode": 200, "body": "Message received"}


    except Exception as e:
        print(f"Error processing event: {e}")
        return {"statusCode": 400, "body": "Invalid event format"}
    



