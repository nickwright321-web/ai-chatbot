# IMPORTANT:
# Mock boto3 BEFORE any application modules are imported.
# This prevents DynamoDB clients from being created during test collection.

import sys
from unittest.mock import MagicMock

# Replace boto3 and botocore with harmless mocks
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()
sys.modules['botocore.exceptions'] = MagicMock()
