import json
import boto3
import os

secrets = boto3.client("secretsmanager")

SECRET_NAME = os.environ.get("SECRET_NAME", "ai-chatbot-websocket-secret")


def lambda_handler(event, context):
    print("Event:", json.dumps(event))

    token = None

    # 1. Extract token from query string
    if event.get("queryStringParameters"):
        token = event["queryStringParameters"].get("token")

    # 2. Or from Authorization header
    if not token and event.get("headers"):
        auth = event["headers"].get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ")[1]

    if not token:
        return deny("Missing token", event)

    # 3. Get expected token (stubbed here)
    try:
        expected_token = "abc123"
        # real version:
        # secret_value = secrets.get_secret_value(SecretId=SECRET_NAME)
        # expected_token = secret_value["SecretString"]
    except Exception as e:
        print("Secrets Manager error:", str(e))
        return deny("Server error", event)

    # 4. Validate
    if token == expected_token:
        return allow("demo-user", event)
    else:
        return deny("Invalid token", event)


def allow(principal_id, event):
    """Allow policy"""
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "*"
                }
            ]
        },
        "context": {
            "principalId": principal_id
        }
    }


def deny(message, event):
    """Deny policy"""
    return {
        "principalId": "unauthorized",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": "*"
                }
            ]
        },
        "context": {
            "error": message
        }
    }