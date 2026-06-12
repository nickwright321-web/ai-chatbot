import json
import os
from connection_handler.app import lambda_handler

# Build path relative to this file
base_dir = os.path.dirname(os.path.abspath(__file__))
event_path = os.path.join(base_dir, "..", "events", "ws_connect_event.json")

with open(event_path) as f:
    event = json.load(f)

context = None

if __name__ == "__main__":
    print(lambda_handler(event, context))
