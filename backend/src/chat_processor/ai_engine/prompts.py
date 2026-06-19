import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

BOB_PROMPT = os.environ.get("BOB_PROMPT", "s3://bob-training-data-132696833143-eu-west-2/bob-prompt.txt")

def getSystemPrompt(aiName: str = "Bob") -> str:
    bucket_name, key = BOB_PROMPT.replace("s3://", "").split("/", 1)
    return load_prompt_from_s3(bucket_name, key)


def getBobPrompt() -> str:
    try:
        bucket_name, key = BOB_PROMPT.replace("s3://", "").split("/", 1)
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        prompt = response["Body"].read().decode("utf-8")
        logger.info("Fetched Bob prompt from S3.")
        return prompt
    except Exception as e:
        logger.error("Fetching Bob prompt:%s", e)
        return "You are Bob, a helpful assistant."


def load_prompt_from_s3(bucket_name, file_key):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        logger.error("Error downloading from S3: %s", e)
        return None
