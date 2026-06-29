import os
import time
import boto3

DEFAULT_TABLE_NAME = os.environ["CONNECTIONS_TABLE_NAME"]

class ConnectionsRepository:
    def __init__(self, table_name=DEFAULT_TABLE_NAME):
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(table_name)

    def put_connection(self, connectionId: str, domain: str, stage: str):
        self.table.put_item(
            Item={
                "connectionId": connectionId,
                "wsDomainName": domain,
                "wsStage": stage,
                "connectedAt": int(time.time())
            }
        )

    def get_connection(self, connectionId: str):
        response = self.table.get_item(
            Key={"connectionId": connectionId}
        )
        return response.get("Item")  # returns dict or None

    def delete_connection(self, connectionId: str):
        self.table.delete_item(
            Key={"connectionId": connectionId}
        )
