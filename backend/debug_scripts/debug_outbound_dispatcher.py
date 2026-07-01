import json
import base64,os
import sys
import os

# Add backend/src to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from outboundMessageDispatcher.app import lambda_handler

class Ctx:
    function_name = "local-test"
    memory_limit_in_mb = 128
    aws_request_id = "local-req-1"

context = Ctx()
class MockGateway:
    def post_to_connection(self, ConnectionId, Data):
        print(f"[MOCK] post_to_connection called:")
        print(f"  ConnectionId = {ConnectionId}")
        print(f"  Data         = {Data.decode('utf-8')}")

# Introduction Event
# with open("backend/events/outbound_dispatcher.json", "r") as f:
with open("backend/events/outbound_dispatcher_agentgreeting.json", "r") as f:
    event = json.load(f)

print("=== Running lambda_handler Introduction ===")
response = lambda_handler(event, context, apigw_client_factory = lambda domain, stage: MockGateway())
print("Lambda returned:", response)