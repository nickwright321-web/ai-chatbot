# ai_engine/factory.py
from .Mistral7b2Engine import MistralEngine
# Add other engines later

def create_engine(engine_name: str):
    engine_name = engine_name.lower()

    if engine_name == "mistral7b2":
        return MistralEngine()

    raise ValueError(f"Unknown engine: {engine_name}")
