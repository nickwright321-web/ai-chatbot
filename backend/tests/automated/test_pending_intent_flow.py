import pytest
import json
import base64
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "src")
sys.path.append(SRC)
import chat_processor.app as app


# ---------------------------------------------------------
# Helper: fake session state object
# ---------------------------------------------------------
class DummyState:
    def __init__(self, pending_intent=None):
        self.pending_intent = pending_intent

    def get(self, key):
        if key == "pending_intent":
            return self.pending_intent
        return None


# ---------------------------------------------------------
# Default: no pending intent
# ---------------------------------------------------------
@pytest.fixture(autouse=True)
def patch_load_state(monkeypatch):
    def fake_load(_connectionId):
        return None
    monkeypatch.setattr(app, "loadSessionState", fake_load)
    return fake_load


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_no_pending_intent_returns_none():
    """No pending intent → always None."""
    result = app.checkPendingIntent("abc", "anything")
    assert result is None


@pytest.mark.parametrize("msg", ["yes", "y", "ok", "sure", "YES", "Ok"])
def test_positive_responses_return_queue(monkeypatch, msg):
    """Pending intent + positive confirmation → QUEUE."""
    def fake_load(_):
        return DummyState("SALES")
    monkeypatch.setattr(app, "loadSessionState", fake_load)

    assert app.checkPendingIntent("abc", msg) == "QUEUE"


@pytest.mark.parametrize("msg", ["no", "n", "NO", "N"])
def test_negative_responses_return_continue(monkeypatch, msg):
    """Pending intent + negative confirmation → CONTINUE."""
    def fake_load(_):
        return DummyState("SALES")
    monkeypatch.setattr(app, "loadSessionState", fake_load)

    assert app.checkPendingIntent("abc", msg) == "CONTINUE"


@pytest.mark.parametrize("msg", ["maybe", "hello", "forward me", "123", ""])
def test_other_responses_return_none(monkeypatch, msg):
    """Pending intent + anything else → None."""
    def fake_load(_):
        return DummyState("SALES")
    monkeypatch.setattr(app, "loadSessionState", fake_load)

    assert app.checkPendingIntent("abc", msg) is None
