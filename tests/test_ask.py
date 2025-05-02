import json
import os


def test_ask_me_anything(monkeypatch, client):
    # Mock the Gemini call
    class DummyResp:
        text = "dummy answer"

    def dummy_generate(**kwargs):
        return DummyResp()

    monkeypatch.setattr(
        "app.api.v1.endpoints.ask.model.generate_content", dummy_generate
    )
    payload = {"question": "What is DNA?"}
    res = client.post("/ask-me-anything/", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "answer" in body and body["answer"] == "dummy answer"
