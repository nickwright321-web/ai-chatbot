import json
import base64,os
from InboundDispatcher.app import lambda_handler


class MockGateway:
    def post_to_connection(self, ConnectionId, Data):
        print(f"[MOCK] post_to_connection called:")
        print(f"  ConnectionId = {ConnectionId}")
        print(f"  Data         = {Data.decode('utf-8')}")

connectionId = base64.urlsafe_b64encode(os.urandom(12)).decode("utf-8") #"gR9cEL5m_leUJAoRIA=="

# Introduction Event
with open("backend/events/inbound_dispatcher_error.json", "r") as f:
    event = json.load(f)
    # event["requestContext"]["connectionId"] = connectionId


# Fake context
class Ctx:
    function_name = "local-test"
    memory_limit_in_mb = 128
    aws_request_id = "local-req-1"

context = Ctx()

print("=== Running lambda_handler Introduction ===")
response = lambda_handler(event, context)
print("Lambda returned:", response)

