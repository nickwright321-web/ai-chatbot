
import logging

#shared util class to keep the Lambda clean
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def LogInfo(message):
    logger.info(message)

def LogError(message):
    logger.error(message)

def LogWarning(message):
    logger.warning(message)