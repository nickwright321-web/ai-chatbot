import json
import logging
import boto3
from .ccAdapter import ccAdapter

logger = logging.getLogger(__name__)

class MockCCAdapter(ccAdapter):
    """
    Mock CCaaS adapter used for demo tenants.
    Instead of calling a real CCaaS platform, it sends a synthetic
    outbound message into the OutboundMessages SQS queue.
    """

    def __init__(self, outbound_queue_url: str):
        self.outbound_queue_url = outbound_queue_url
        self.sqs = boto3.client("sqs")

    def prepare_payload(self, message: dict) -> dict:
        """
        For a mock adapter, we simply pass the message through.
        """
        return message

    def deliver(self, prepared_message: dict):
        """
        Instead of calling a CCaaS API, we generate a mock outbound
        message and push it into the outbound SQS queue.
        """

        logger.info("[DemoCompAdapter] Generating mock CCaaS response")

        outbound_message = {
            "companyId": prepared_message["companyId"],
            "connectionId": prepared_message["connectionId"],
            "direction": "Outbound",
            "text": f"DemoComp mock reply to: {prepared_message['userMessage']}",
            "timestamp": prepared_message.get("timestamp")
        }

        logger.info(f"[DemoCompAdapter] Sending mock message to outbound queue: {outbound_message}")

        self.sqs.send_message(
            QueueUrl=self.outbound_queue_url,
            MessageBody=json.dumps(outbound_message)
        )

        return {"status": "mocked", "sentTo": "OutboundMessagesQueue"}

    def handle_error(self, original_message: dict, error: Exception):
        logger.error(f"[DemoCompAdapter] Mock adapter failed: {error}")
