import json
import base64,os
from chat_processor.app import lambda_handler as chat_proc
from intent_router.app import lambda_handler as int_rout


class MockGateway:
    def post_to_connection(self, ConnectionId, Data):
        print(f"[MOCK] post_to_connection called:")
        print(f"  ConnectionId = {ConnectionId}")
        print(f"  Data         = {Data.decode('utf-8')}")

connectionId = base64.urlsafe_b64encode(os.urandom(12)).decode("utf-8") #"gR9cEL5m_leUJAoRIA=="

# error_event = {
#     "requestContext": {
#         "routeKey": "sendMessage",
#         "authorizer": {
#             "companyId": "BigCorp",
#             "principalId": "demo-user"
#         },
#         "messageId": "gR5bSU5hOWeIKAIdeA==",
#         "eventType": "MESSAGE",
#         "extendedRequestId": "fbVBOFg1rPEEt3A=",
#         "requestTime": "23/Jun/2026:18:22:12 +0000",
#         "messageDirection": "IN",
#         "stage": "prod",
#         "connectedAt": 1782238926413,
#         "requestTimeEpoch": 1782238932290,
#         "identity": {
#             "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0",
#             "sourceIp": "64.227.39.60"
#         },
#         "requestId": "fbVBOFg1rPEEt3A=",
#         "domainName": "rzif0hduhj.execute-api.eu-west-2.amazonaws.com",
#         "connectionId": "gR5bQg5gDWeIKAIdeA==",
#         "apiId": "rzif0hduhj"
#     },
#     "body": "{\"action\":\"sendMessage\",\"message\":\"hi\"}",
#     "isBase64Encoded": "false"
# }

# # Fake context
# class Ctx:
#     function_name = "local-test"
#     memory_limit_in_mb = 128
#     aws_request_id = "local-req-1"

# context = Ctx()


# response = response = chat_proc(error_event, context, apigw_client_factory = lambda domain, stage: MockGateway())

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
response = chat_proc(event, context, apigw_client_factory = lambda domain, stage: MockGateway())
print("Lambda returned:", response)


with open("backend/events/ws_valid_IT_Tech_question.json", "r") as f:
    event = json.load(f)
    event["requestContext"]["connectionId"] = connectionId


print("=== Running lambda_handler Valid question ===")
response = chat_proc(event, context, apigw_client_factory = lambda domain, stage: MockGateway())
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
response = chat_proc(event, context, apigw_client_factory = lambda domain, stage: MockGateway())
print("Lambda returned:", response)

# Intent router receives payload from InboundMessages queue
with open("backend/events/intent_router_forward_to_tech_support.json", "r") as f:
    event = json.load(f)

print("=== Running lambda_handler Invalid question ===")
response = int_rout(event, context)
print("Lambda returned:", response)

