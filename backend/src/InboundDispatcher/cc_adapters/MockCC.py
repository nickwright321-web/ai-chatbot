import json
import logging
import boto3
from .ccAdapter import ccAdapter
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MockCCAdapter(ccAdapter):
    
    # Company routing assesses which companies use this system and what
    # queries they will handle (to be implemented)'
    # Future improvement: store in a config table!
    
    ROUTING = [
                {   "companyId": "BigCorp",
                    "intent": ["TECH_SUPPORT", "SALES"],
                    "outboundQueueUrl": "http://"
                },
                {   "companyId": "LittleCorp",
                    "intent": ["TECH_SUPPORT", "SALES"],
                    "outboundQueueUrl": "http://"
                }
    ]

    integrationId = "aabfasd"

    
    def _extract_ordered_messages(self,chat_history: list[dict]) -> list[str]:
        # Sort by timestamp (ascending)
        sorted_history = sorted(chat_history, key=lambda x: x["timestamp"])
        # Extract connectionId from the first message
        connection_id = sorted_history[0]["connectionId"]

        # Build transcript lines
        lines = [f"{item['role']}: {item['message']}" for item in sorted_history]

        # Join into a single transcript string
        transcript = "\n".join(lines)

        return {
            "connectionId": connection_id,
            "transcript": transcript
        }

    def _prepare_payload(self, message: dict) -> dict:
        chatHistory = message["transcript"]
        connectionId = message["connectionId"]

        logger.info(f"Message: {chatHistory}")

        return {
            "from": {
                "id": connectionId,
                "type": "web"
            },
            "to": {
                "id": self.integrationId,
                "type": "open"
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "text": "Conversation Summary",  # the latest message
            "direction": "Inbound",
            "metadata": {
                "context": f"Chat history:\n{chatHistory}",
                "connectionId": connectionId
            }
        }

    def _deliver(self, prepared_message: dict):  
       
        logger.info(f"[DemoCompAdapter] Sending mock message to outbound queue: {prepared_message}")

        self.sqs.send_message(
            QueueUrl=self.outbound_queue_url,
            MessageBody=json.dumps(prepared_message)
        )

        return {"status": "mocked", "sentTo": "OutboundMessagesQueue"}

    def handle_error(self, original_message: dict, error: Exception):
        logger.error(f"[DemoCompAdapter] Mock adapter failed: {error}")
