import os
import json
import boto3

#MODEL_ID = os.environ.get("MODEL_ID", "mistral.mistral-large-2402-v1:0")

MODEL_ID = "mistral.mistral-7b-instruct-v0:2"


#bedrock = boto3.client("bedrock-runtime")

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
            agentName = "Bob"
            ai_reply = callBob(message)
            reply = {   "agentName": agentName,
                        "message": ai_reply
                    }
          
            apigw.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(reply).encode("utf-8")
            )
            print("Message sent OK")
        except Exception as e:
            print("Error sending message:", e)



        return {"statusCode": 200, "body": "Message received"}


    except Exception as e:
        print(f"Error processing event: {e}")
        return {"statusCode": 400, "body": "Invalid event format"}
    


def callBob(user_message: str) -> str:
    """
    Sends the user message to Claude 3 Sonnet via Bedrock
    and returns the bot's reply.
    """
    try:
        bedrock = boto3.client("bedrock-runtime", region_name="eu-west-2")
        print("Bedrock client endpoint:", bedrock._endpoint.host)

        response = bedrock.invoke_model(
            modelId=MODEL_ID,
           body=json.dumps({
                "prompt": f"You are Bob, answer the user in one sentence and do not give any custom responses.\n\nUser: {user_message}\nAssistant:",
                "max_tokens": 50
            })
        )


        model_response = json.loads(response["body"].read())
        ai_text = model_response['outputs'][0]['text']

        print("Bedrock model response:", ai_text)

        return ai_text

    except Exception as e:
        print("Bedrock error:", e)
        return "Sorry, I had trouble generating a response."
