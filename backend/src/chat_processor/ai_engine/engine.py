import boto3
import logging
from  ..ChatMessage import ChatMessage
from .prompts import getSystemPrompt, load_prompt_from_s3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MODEL_ID = "mistral.mistral-7b-instruct-v0:2"
AI_NAME = "Bob"

def sendToAI(userMessage: str, chatHistory: list) -> ChatMessage:
    try:
        bedrock = boto3.client("bedrock-runtime", region_name="eu-west-2")

        system_prompt = getSystemPrompt(AI_NAME)
        if not system_prompt:
            system_prompt = f"You are {AI_NAME}, a helpful assistant."

        # Build raw messages
        raw_messages = []
        for item in chatHistory:
            hf_role = "user" if item["role"].lower() == "user" else "assistant"
            raw_messages.append({"role": hf_role, "content": item["message"]})

        raw_messages.append({"role": "user", "content": userMessage})

        cleaned_history: list[dict[str, str]] = []
        for msg in raw_messages:
            if cleaned_history and cleaned_history[-1]["role"] == msg["role"]:
                cleaned_history[-1]["content"] += f"\n{msg['content']}"
            else:
                cleaned_history.append(msg)

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

        response = bedrock.converse(
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

        ai_text = processAIResponse(response)
        return formatAIMessage(ai_text)

    except Exception as e:
        logger.error("Bedrock error:%s", e)
        return ChatMessage(text="Sorry, I had trouble generating a response.", intent="ERROR")

def processAIResponse(response: dict) -> str:
    content = response.get("output", {}).get("message", {}).get("content", [])
    return_text = ""

    if not content:
        return "I'm sorry, I don't know how to help"

    for block in content:
        if isinstance(block, dict) and "text" in block:
            return_text = block["text"].strip()

    return return_text.encode('ascii', 'ignore').decode('ascii')

def formatAIMessage(message: str) -> ChatMessage:
    if "<INTENT:" not in message:
        return ChatMessage(text=message.strip(), intent="NO_INTENT")

    text, intent_part = message.split("<INTENT:", 1)
    intent = intent_part.replace(">", "").strip()

    return ChatMessage(text=text.strip(), intent=intent)
