import asyncio
import websockets
import json

WS_URL = "wss://t06c9a550e.execute-api.eu-west-2.amazonaws.com/prod"

async def test():
    async with websockets.connect(WS_URL) as ws:
        print("Connected")

        # Send a message to your route
        await ws.send(json.dumps({
          "action": "sendMessage",
          "message": "Hello from test client"
        }))

        try:
          # Wait for a response
          response = await asyncio.wait_for(ws.recv(), timeout=3)
          print("Received:", response)
        except asyncio.TimeoutError:
          print("No response received within timeout")

asyncio.run(test())
