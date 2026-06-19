import json
import base64,os
from chat_processor.app import lambda_handler


class MockGateway:
    def post_to_connection(self, ConnectionId, Data):
        print(f"[MOCK] post_to_connection called:")
        print(f"  ConnectionId = {ConnectionId}")
        print(f"  Data         = {Data.decode('utf-8')}")



connectionId = base64.urlsafe_b64encode(os.urandom(12)).decode("utf-8") #"gR9cEL5m_leUJAoRIA=="

# Introduction Event
with open("backend/events/ws_introduction.json", "r") as f:
    event = json.load(f)
    event["requestContext"]["connectionId"] = connectionId


# Fake context
class Ctx:
    function_name = "local-test"
    memory_limit_in_mb = 128
    aws_request_id = "local-req-1"

context = Ctx()

print("=== Running lambda_handler Introduction ===")
response = lambda_handler(event, context, apigw_client_factory = lambda domain, stage: MockGateway())
print("Lambda returned:", response)


with open("backend/events/ws_valid_IT_Tech_question.json", "r") as f:
    event = json.load(f)
    event["requestContext"]["connectionId"] = connectionId


print("=== Running lambda_handler Valid question ===")
response = lambda_handler(event, context, apigw_client_factory = lambda domain, stage: MockGateway())
print("Lambda returned:", response)


# with open("backend/events/ws_invalid_question.json", "r") as f:
#     event = json.load(f)
#     event["requestContext"]["connectionId"] = connectionId

# #asks for help -> forward to Genesys
# with open("backend/events/ws_accepts_help.json", "r") as f:
#     event = json.load(f)
#     event["requestContext"]["connectionId"] = connectionId
    

#asks for help -> forward to Genesys
with open("backend/events/ws_accepts_help.json", "r") as f:
    event = json.load(f)
    event["requestContext"]["connectionId"] = connectionId

print("=== Running lambda_handler Invalid question ===")
response = lambda_handler(event, context, apigw_client_factory = lambda domain, stage: MockGateway())
print("Lambda returned:", response)

