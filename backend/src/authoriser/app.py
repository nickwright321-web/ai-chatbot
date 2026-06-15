import json
import boto3
import os

secrets = boto3.client("secretsmanager")

# Name of the secret in Secrets Manager
SECRET_NAME = os.environ.get("SECRET_NAME", "ai-chatbot-websocket-secret")

def lambda_handler(event, context):
    """
    Simple WebSocket Lambda Authorizer.
    Validates a token against a secret stored in AWS Secrets Manager.
    """

    print("Event:", json.dumps(event))

    # 1. Extract token from querystring or Authorization header
    token = None

    if event.get("queryStringParameters"):
        token = event["queryStringParameters"].get("token")

    if not token and event.get("headers"):
        auth = event["headers"].get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ")[1]

    if not token:
        return deny("Missing token")

    # 2. get the secret
    try:
        secret_value = secrets.get_secret_value(SecretId=SECRET_NAME)
        expected_token = secret_value["SecretString"]
    except Exception as e:
        print("Secrets Manager error:", str(e))
        return deny("Server error")

    # 3. Compare
    if token == expected_token:
        return allow("demo-user")
    else:
        return deny("Invalid token")


def allow(principal_id):
    """Return IAM policy that ALLOWS the WebSocket connection."""
    return {
        "isAuthorized": True,
        "context": {
            "principalId": principal_id
        }
    }


def deny(message):
    """Return IAM policy that DENIES the WebSocket connection."""
    return {
        "isAuthorized": False,
        "context": {
            "error": message
        }
    }
