
def formatAIMessage(message: str) -> dict:
    if "<INTENT:" not in message:
        return {"text": message.strip(), "intent": None}

    text, intent_part = message.split("<INTENT:", 1)
    intent = intent_part.replace(">", "").strip()

    return {
        "text": text.strip(),
        "intent": intent
    }



ai_response =  "Hi, I'm Bob. How can I help today?<INTENT: GENERAL_ENQUIRY>"

print("ai_response", ai_response)

formattedMessage = formatAIMessage(ai_response)

print (f"Message text: {formattedMessage["text"]}, Intent: {formattedMessage["intent"]}")
