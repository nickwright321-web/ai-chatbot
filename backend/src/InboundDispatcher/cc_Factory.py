import os
from backend.src.InboundDispatcher.cc_adapters.Genesys import GenesysAdapter
from backend.src.InboundDispatcher.cc_adapters.MockCC import MockCCAdapter

OUTBOUND_SQS_QUEUE = os.environ.get("OUTBOUND_SQS_QUEUE", "OutbondQueue")

COMPANY_TO_UC = {
    "DemoComp": "mockcc",
    "BigCorp": "zoom",
}

ADAPTERS = {
    "genesys": GenesysAdapter,
    "mockcc": MockCCAdapter
}

def get_adapter(company_id):
    uc = COMPANY_TO_UC.get(company_id)
    if not uc:
        raise ValueError(f"No UC platform configured for company {company_id}")
    
    if uc == "genesys":
        return GenesysAdapter(
            region="eu-west-2",
            client_id=os.environ["GENESYS_CLIENT_ID"],
            client_secret=os.environ["GENESYS_CLIENT_SECRET"],
            integration_id=os.environ["GENESYS_INTEGRATION_ID"]
        )
    
    if uc == "mockcc":
        return MockCCAdapter(OUTBOUND_SQS_QUEUE)

    return ADAPTERS[uc]()
