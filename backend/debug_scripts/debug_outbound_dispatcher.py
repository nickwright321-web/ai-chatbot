import json
import base64,os
import sys
import os

# Add backend/src to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from outboundMessageDispatcher.app import lambda_handler

# Introduction Event
with open("backend/events/outbound_dispatcher.json", "r") as f:
    event = json.load(f)

print("=== Running lambda_handler Introduction ===")
response = lambda_handler(event, None)
print("Lambda returned:", response)

