import boto3

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