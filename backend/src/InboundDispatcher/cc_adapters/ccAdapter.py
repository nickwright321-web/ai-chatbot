import logging
from abc import ABC, abstractmethod
from typing import final

logger = logging.getLogger(__name__)

class ccAdapter(ABC):
    ###
    # Base class for all Contact Centre platform adapters.
    # Each adapter must implement #
    #   prepare_payload() to format the message for the CC
    #   deliver() to send the message to the specific cc platform (Genesys, Zoom, etc.).
    #   send_message() so the caller can send the message
    #   ROUTING - so the cc factory can determine which adapter to use
    ###

    def __init__(self, outbound_queue_url: str):
        self._outbound_queue_url = outbound_queue_url
        
    @property
    @abstractmethod
    def ROUTING(self) -> dict:
        
        # Each adapter MUST define a ROUTING dict:
        # {
        #     "companyId": [...],
        #     "intent": [...]
        # }
        
        pass

    @final
    def send_message(self, messages: list[dict]):
        ###########
        # Used by the dispatcher to deliver prepare and deliver the message
        ##############
        try:
            logger.info(f"[{self.__class__.__name__}] Received message for delivery")

            if not messages:
                logger.info("No messages to send")#
                return None

            ordered_message = self._extract_ordered_messages(messages)

            prepared = self._prepare_payload(ordered_message)
            logger.debug(f"[{self.__class__.__name__}] Prepared payload: {prepared}")

            response = self._deliver(prepared)
            logger.info(f"[{self.__class__.__name__}] Delivery successful")

            return response

        except Exception as e:
            logger.error(
                f"[{self.__class__.__name__}] Delivery failed: {e}",
                exc_info=True
            )
            self.handle_error(messages, e)
            raise

    
    @abstractmethod
    def _extract_ordered_messages(self,chat_history: list[dict]) -> list[str]:
        return chat_history
    
    @abstractmethod
    def _prepare_payload(self, message: dict) -> dict:        
        return message

    @abstractmethod
    def _deliver(self, prepared_message: dict):
        ###
        ### internal method for delivering the message to the CC Platform
        ###
        
        pass

    def handle_error(self, original_message: dict, error: Exception):
        
        logger.warning(
            f"[{self.__class__.__name__}] Not implemented"
        )
