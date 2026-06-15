import json
from chat_processor.app import lambda_handler

# Fake WebSocket event
event = {
    "requestContext": {
        "routeKey": "sendMessage",
        "connectionId": "test-connection-123",
        "domainName": "localhost",
        "stage": "dev"
    },
    "body": json.dumps({
        "message": "Hello Bob!"
    })
}

# Fake context
class Ctx:
    function_name = "local-test"
    memory_limit_in_mb = 128
    aws_request_id = "local-req-1"

context = Ctx()

print("=== Running lambda_handler ===")
response = lambda_handler(event, context)
print("Lambda returned:", response)

print("\n=== Testing callBob() ===")
reply = callBob("Tell me a joke")
print("AI reply:", reply)
