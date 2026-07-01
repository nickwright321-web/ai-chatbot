#initialise the logger
import logging,json,boto3

from shared.Gateway import Gateway
from shared.ConnectionsRepository import ConnectionsRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_apigw_client(domain, stage):
    return boto3.client(
        "apigatewaymanagementapi",
        endpoint_url=f"https://{domain}/{stage}"
    )

def lambda_handler(event, context, apigw_client_factory=get_apigw_client):
    #inject the gateway client so it can be mocked when testing
    
    connRepo = ConnectionsRepository()

    try:
        event_json = json.dumps(event, separators=(",", ":"))
        logger.info(f"EVENT: {event_json}")
        
        records = event["Records"]

        for record in records:    
            message:str = ""
            connectionId:str = ""
            agentName:str = ""
            text:str = ""
            
            body = json.loads(record["body"])
            if (body) is None:
                raise Exception("Missing Body")

            try:
                message = body["message"]
            except json.JSONDecodeError:
                raise Exception("Body is not valid JSON")

            if(message := body.get("message")) is None:
                raise Exception("No message received")
            
            if(connectionId := body.get("connectionId")) is None:
                raise Exception("No connection ID received")
            
            if(text := message.get("text")) is None:
                raise Exception("No text received")
            
            if(agentName := message.get("agentName")) is None:
                raise Exception("No agent name received")

            break
            #Only one message has been sent, so break the for loop
            #as soon as you get the connectionId and text of the message

        #retrieve the connection info from the connections repository to
        #get the API Gateway domain and stage for the connection
        
        logger.info(f"Retrieving connection info: Connection ID: {connectionId}")
        conn = connRepo.get_connection(connectionId)
        logger.info(f"Connection Info retrieved successfully: Connection ID: {connectionId}")
        
        #post to the client using the API Gateway Management API
        Gateway.init(apigw_client_factory(conn["wsDomainName"], conn["wsStage"]))
        logger.info(f"Posting message to client: Connection ID: {connectionId}, Message: {text}")
        Gateway.post(agentName, text, connectionId)

    except Exception as e:
        logger.error(f"ERROR: {e}::: {event_json}")


