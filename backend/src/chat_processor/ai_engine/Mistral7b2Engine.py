import boto3
import logging
import json
from ..ChatMessage import ChatMessage
from .base import AIEngine
from .prompts import getSystemPrompt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MODEL_ID = "mistral.mistral-7b-instruct-v0:2"
AI_NAME = "Bob"

class MistralEngine(AIEngine):
    def __init__(self):
        self.client = boto3.client("bedrock-runtime", region_name="eu-west-2")

    def sendToAI(self, userMessage: str, chatHistory: list) -> ChatMessage:
        try:
            system_prompt = getSystemPrompt(AI_NAME)
            if not system_prompt:
                system_prompt = f"You are {AI_NAME}, a helpful assistant."

            # Convert chat history to HF-style messages
            raw_messages = []
            for item in chatHistory:
                hf_role = "user" if item["role"].lower() == "user" else "assistant"
                raw_messages.append({"role": hf_role, "content": item["message"]})

            raw_messages.append({"role": "user", "content": userMessage})

            # Merge consecutive roles
            cleaned_history = []
            for msg in raw_messages:
                if cleaned_history and cleaned_history[-1]["role"] == msg["role"]:
                    cleaned_history[-1]["content"] += f"\n{msg['content']}"
                else:
                    cleaned_history.append(msg)

            # Only include user messages in the final prompt
            cleaned_history_text = "\n".join(
                msg["content"] for msg in cleaned_history if msg["role"] == "user"
            )

            full_prompt = (
                system_prompt
                + "\n\n"
                + cleaned_history_text
                + "\n\nUser: "
                + userMessage
            )

            response = self.client.converse(
                modelId=MODEL_ID,
                messages=[{"role": "user", "content": [{"text": full_prompt}]}],
                guardrailConfig={
                    "guardrailIdentifier": "ekricr3x6tsa",
                    "guardrailVersion": "2"
                },
                inferenceConfig={
                    "maxTokens": 50,
                    "temperature": 0.2,
                    "stopSequences": ["User:", "\nUser:", "\n\nUser"]
                }
            )

            ai_text = self._processAIResponse(response)
            return self._formatAIMessage(ai_text)

        except Exception as e:
            logger.error("Bedrock error: %s", e)
            return ChatMessage(text="Sorry, I had trouble generating a response.", intent="ERROR")

    # -------------------------
    # Internal helpers
    # -------------------------

    def _processAIResponse(self, response: dict) -> str:
        content = response.get("output", {}).get("message", {}).get("content", [])
        if not content:
            return "I'm sorry, I don't know how to help"

        for block in content:
            if isinstance(block, dict) and "text" in block:
                text = block["text"].strip()
                return text.encode('ascii', 'ignore').decode('ascii')

        return "I'm sorry, I don't know how to help"

    def _formatAIMessage(self, message: str) -> ChatMessage:
        if "<INTENT:" not in message:
            return ChatMessage(text=message.strip(), intent="NO_INTENT")

        text, intent_part = message.split("<INTENT:", 1)
        intent = intent_part.replace(">", "").strip()

        return ChatMessage(text=text.strip(), intent=intent)
