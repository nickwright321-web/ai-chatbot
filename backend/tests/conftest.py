import pytest
import boto3

# mock boto3 class for running tests from github

@pytest.fixture(autouse=True)
def mock_boto3(monkeypatch):
    """Prevent boto3 from creating real AWS clients during tests."""

    class DummyResource:
        def Table(self, name):
            return None

    def fake_resource(*args, **kwargs):
        return DummyResource()

    monkeypatch.setattr(boto3, "resource", fake_resource)
