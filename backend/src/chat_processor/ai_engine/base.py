# ai_engine/base.py
from abc import ABC, abstractmethod

class AIEngine(ABC):
    """Base class for all AI model engines."""

    @abstractmethod
    def sendToAI(self, prompt: str, system: str = None) -> str:
        """Generate a response from the model."""
        pass
