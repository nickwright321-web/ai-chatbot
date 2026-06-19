from dataclasses import dataclass, asdict

@dataclass
class ChatMessage:
    text: str
    intent: str
