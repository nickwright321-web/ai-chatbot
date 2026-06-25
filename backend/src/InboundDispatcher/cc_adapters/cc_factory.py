import logging
from InboundDispatcher.cc_adapters import ALL_ADAPTERS


logger = logging.getLogger(__name__)
        
def getAdapter(companyId:str):
     
    for adapter in ALL_ADAPTERS:
        logger.info(f"Assessing adapter {adapter}")
        for rule in adapter.ROUTING:
            if rule["companyId"] == companyId:

                # Create an instance
                returnAdapter = adapter(rule["outboundQueueUrl"])
                return returnAdapter
          
    return None