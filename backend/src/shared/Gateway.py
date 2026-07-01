import boto3, json

class Gateway:
    _client = None

    @classmethod
    def init(cls, client):
        cls._client = client
    
    @classmethod
    def get(cls):
        if cls._client is None:
            raise RuntimeError("Gateway client not initialised")
        return cls._client
    
    @classmethod
    def post(cls, agentName: str, message: str, connectionId: str):
        if cls._client is None:
            raise RuntimeError("Gateway client not initialised")

        payload = {
            "agentName": agentName,
            "message": message
        }

        cls._client.post_to_connection(
            ConnectionId=connectionId,
            Data=json.dumps(payload).encode("utf-8")
        )