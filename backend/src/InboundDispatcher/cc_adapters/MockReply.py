import json
import boto3
import urllib.request
import urllib.parse
import base64

COGNITO_DOMAIN = "https://livechat-auth-132696833143.auth.eu-west-2.amazoncognito.com"
REGION="eu-west-2"
SECRET_NAME="ai-chatbot-api-creds"
API_URL = "https://gsac5us527.execute-api.eu-west-2.amazonaws.com/Prod/outboundMessage"

def get_secret():
    client = boto3.client("secretsmanager", region_name=REGION)

    response = client.get_secret_value(SecretId=SECRET_NAME)
    secret = json.loads(response["SecretString"])

    return secret["client_id"], secret["client_secret"]

def http_post_form(url, data, client_id, client_secret):
    encoded_data = urllib.parse.urlencode(data).encode("utf-8")

    req = urllib.request.Request(url, data=encoded_data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    # Basic auth for Cognito
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req.add_header("Authorization", f"Basic {auth}")

    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def http_post_json(url, payload, token):
    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req, timeout=10) as resp:
        return {
            "statusCode": resp.status,
            "body": resp.read().decode("utf-8")
        }

def get_token():
    client_id, client_secret = get_secret()

    url = f"{COGNITO_DOMAIN}/oauth2/token"

    data = {
        "grant_type": "client_credentials",
        "scope": "outbound-api/read"
    }

    response = http_post_form(url, data, client_id, client_secret)

    return response["access_token"]

def send_message(message: dict):
    token = get_token()

    payload = {
        "message": message
    }

    return http_post_json(API_URL, payload, token)

if __name__ == "__main__":
    send_message("Hello from Python 🚀")