import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ccAdapter(ABC):
    """
    Base class for all Contact Centre platform adapters.
    Each adapter must implement the deliver() method to send the
    message to the specific cc platform (Genesys, Zoom, etc.).
    """

    def send_message(self, message: dict):
        ###########
        # Used by the dispatcher to deliver prepare and deliver the message
        ##############
        try:
            logger.info(f"[{self.__class__.__name__}] Received message for delivery")

            prepared = self.prepare_payload(message)
            logger.debug(f"[{self.__class__.__name__}] Prepared payload: {prepared}")

            response = self.deliver(prepared)
            logger.info(f"[{self.__class__.__name__}] Delivery successful")

            return response

        except Exception as e:
            logger.error(
                f"[{self.__class__.__name__}] Delivery failed: {e}",
                exc_info=True
            )
            self.handle_error(message, e)
            raise

    def prepare_payload(self, message: dict) -> dict:
        ###
        ### transforms the message into the platform specific format
        ###
        return message

    @abstractmethod
    def deliver(self, prepared_message: dict):
        """
        Must be implemented by each CCaaS adapter.
        This method performs the actual API call / SDK call.
        """
        pass

    def handle_error(self, original_message: dict, error: Exception):
        """
        Optional hook for custom error handling.
        Override if you want retries, DLQ routing, etc.
        """
        logger.warning(
            f"[{self.__class__.__name__}] No custom error handler implemented"
        )
