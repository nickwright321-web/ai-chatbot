# backend/tests/chat_flow_runner.py

import json
import base64
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "src")
sys.path.append(SRC)
import chat_processor.app as app

from chat_processor.ChatMessage import ChatMessage

class MockAIEngine:
    def __init__(self, runner):
        self.runner = runner

    def sendToAI(self, message, history):
        intent = self._classify_intent(message)

        # Build a realistic AI reply
        reply_text = self._build_reply(intent)

        # Store intent for test assertions
        self.runner.last_intent = intent

        return ChatMessage(text=reply_text, intent=intent)

    def _classify_intent(self, message: str) -> str:

        msg = message.lower().strip()

        # 1. Welcome intent
        if msg in ("hi", "hello", "hey", "good morning", "good afternoon", "good evening"):
            return "WELCOME"

        # 2. Tech support keywords
        tech_words = ["error", "issue", "problem", "broken", "not working", "support", "help", "fix"]
        if any(w in msg for w in tech_words):
            return "TECH_SUPPORT"

        # 3. Sales keywords
        sales_words = ["price", "cost", "buy", "purchase", "quote", "upgrade", "subscription"]
        if any(w in msg for w in sales_words):
            return "SALES"

        # 4. Default fallback
        return "GENERAL_ENQUIRY"

    def _build_reply(self, intent: str) -> str:
        if intent == "WELCOME":
            return "Hello! How can I help you today?\n<INTENT: WELCOME>"

        if intent == "TECH_SUPPORT":
            return "I'm sorry you're having trouble. I can help with technical support.\n<INTENT: TECH_SUPPORT>"

        if intent == "SALES":
            return "I can help you with pricing or product information.\n<INTENT: SALES>"

        return "How can I help you today?\n<INTENT: GENERAL_ENQUIRY>"

class MockGateway:
    def __init__(self):
        self.messages = []

    def post_to_connection(self, ConnectionId, Data):
        decoded = json.loads(Data.decode("utf-8"))
        print(f"[MOCK] → {decoded}")
        self.messages.append(decoded)

class MockContext:
    function_name = "local-test"
    memory_limit_in_mb = 128
    aws_request_id = "local-req-1"

class ChatFlowRunner:
    def __init__(self):
        self.connection_id = base64.urlsafe_b64encode(os.urandom(12)).decode("utf-8")
        self.context = MockContext()
        self.gateway = MockGateway()
        self.last_intent = None

        app.get_engine = self._mock_engine_factory

        app.Gateway.init(self.gateway)


    def _mock_engine_factory(self):
        return MockAIEngine(self)   

    def load_event(self, filename):
        path = os.path.join("backend", "events", filename)
        with open(path, "r") as f:
            event = json.load(f)
            event["requestContext"]["connectionId"] = self.connection_id
            return event

    def send_event(self, filename):
        print(f"\n=== EVENT: {filename} ===")
        event = self.load_event(filename)
        response = app.lambda_handler(
            event,
            self.context,
            apigw_client_factory=lambda domain, stage: self.gateway
        )
        print("Lambda returned:", response)
        return response

def send_text(self, text):
    event = {
        "requestContext": {
            "routeKey": "$default",
            "connectionId": self.connection_id,
            "domainName": "localhost",
            "stage": "dev"
        },
        "body": json.dumps({"message": text})
    }

    return lambda_handler(
        event,
        self.context,
        apigw_client_factory=lambda d, s: self.gateway
    )
