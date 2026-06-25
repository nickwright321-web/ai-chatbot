import logging
import requests
from .ccAdapter import ccAdapter

logger = logging.getLogger(__name__)

class GenesysAdapter(ccAdapter):
  
    ROUTING = [
                    {   "companyId": "BigGenCorp",
                        "intent": ["TECH_SUPPORT", "SALES"],
                        "outboundQueueUrl": "http://"
                    },
                    {   "companyId": "InternationalCouriers",
                        "intent": ["SHIPPING", "ORDERS"],
                        "outboundQueueUrl": "http://"
                    }
                ]
                


    def __init__(self, region: str, client_id: str, client_secret: str, integration_id: str):
        self.region = region
        self.client_id = client_id
        self.client_secret = client_secret
        self.integration_id = integration_id
        self.token = None

    # ---------------------------------------------------------
    # 1. AUTHENTICATION
    # ---------------------------------------------------------
    def _authenticate(self):
        
        #use client credentials OAuth
        url = f"https://login.{self.region}.genesyscloud.com/oauth/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        logger.info("GenesysAdapter - Requesting OAuth token")

        response = requests.post(url, data=data)
        response.raise_for_status()

        self.token = response.json()["access_token"]
        logger.info("GenesysAdapter - OAuth token acquired")

    def _get_headers(self):
        if not self.token:
            self._authenticate()

        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _extract_ordered_messages(chat_history: list[dict]) -> list[str]:
        pass

    def _prepare_payload(self, message: dict) -> dict:

        #
        # Converts your internal message format into the
        # Genesys Open Messaging format.
        #

        return {
            "from": {
                "id": message["connectionId"],     # Unique user identifier
                "type": "web"                      # Channel type
            },
            "to": {
                "id": self.integration_id,         # Genesys integration ID
                "type": "open"                     # Always "open"
            },
            "timestamp": message.get("timestamp"),
            "text": message["userMessage"],
            "direction": "Inbound"
        }

    def _deliver(self, prepared_message: dict):
        """
        Sends the prepared message to the Genesys Open Messaging API.
        """

        url = (
            f"https://api.{self.region}.genesyscloud.com/"
            f"api/v2/conversations/messages/inbound/open"
        )

        headers = self._get_headers()

        logger.info(f"[GenesysAdapter] Sending message to Genesys: {prepared_message}")

        response = requests.post(url, json=prepared_message, headers=headers)

        if response.status_code >= 400:
            logger.error(
                f"[GenesysAdapter] Genesys API error {response.status_code}: {response.text}"
            )
            response.raise_for_status()

        logger.info("[GenesysAdapter] Message delivered successfully")
        return response.json()

    def handle_error(self, original_message: dict, error: Exception):
        logger.error(
            f"[GenesysAdapter] Failed to deliver message for company "
            f"{original_message.get('companyId')}: {error}"
        )
