from __future__ import annotations

from src.llm_client import LLMClient
from src.providers import StaticMockProvider


def _client_without_init() -> LLMClient:
    return object.__new__(LLMClient)


def test_parse_response_accepts_valid_json() -> None:
    client = _client_without_init()
    result = client._parse_response(
        '{"recommended_status":"Closed","classification":"True Positive","comment":"Confirmed malicious activity."}'
    )

    assert result == {
        "recommended_status": "Closed",
        "classification": "True Positive",
        "comment": "Confirmed malicious activity.",
    }


def test_parse_response_extracts_json_from_wrapped_text() -> None:
    client = _client_without_init()
    result = client._parse_response(
        'Result follows: {"recommended_status":"Active","classification":"Undetermined","comment":"Needs review."}'
    )

    assert result["recommended_status"] == "Active"
    assert result["classification"] == "Undetermined"
    assert result["comment"] == "Needs review."


def test_parse_response_fails_safe_on_invalid_values() -> None:
    client = _client_without_init()
    result = client._parse_response(
        '{"recommended_status":"Delete","classification":"Malicious","comment":""}'
    )

    assert result == {
        "recommended_status": "Active",
        "classification": "Unspecified",
        "comment": "No analyst-facing explanation was provided by the LLM.",
    }


def test_parse_response_fails_safe_on_non_json() -> None:
    client = _client_without_init()
    result = client._parse_response("not-json")

    assert result["recommended_status"] == "Active"
    assert result["classification"] == "Unspecified"
    assert "could not be parsed" in result["comment"]


def test_analyse_incident_redacts_sensitive_values_before_provider_call() -> None:
    captured: dict[str, str] = {}

    class CapturingProvider:
        def complete(
            self,
            *,
            prompt: str,
            model_name: str,
            temperature: float,
            max_tokens: int,
        ) -> str:
            del model_name, temperature, max_tokens
            captured["prompt"] = prompt
            return '{"recommended_status":"Active","classification":"Undetermined","comment":"Analyst review required."}'

    client = LLMClient(model_name="fake-model", provider=CapturingProvider())

    result = client.analyse_incident(
        "Analyst analyst@example.com observed token=abc123",
        "Connection from 10.10.10.10 with password=hunter2",
    )

    prompt = captured["prompt"]
    assert "analyst@example.com" not in prompt
    assert "abc123" not in prompt
    assert "10.10.10.10" not in prompt
    assert "hunter2" not in prompt
    assert "[REDACTED_EMAIL]" in prompt
    assert "[REDACTED_SECRET]" in prompt
    assert "[REDACTED_IP]" in prompt
    assert "[REDACTED_PASSWORD]" in prompt
    assert result["classification"] == "Undetermined"


def test_static_mock_provider_can_drive_deterministic_llm_result() -> None:
    client = LLMClient(
        model_name="mock-model",
        provider=StaticMockProvider(
            '{"recommended_status":"Active","classification":"Undetermined","comment":"Mock benchmark result."}'
        ),
    )

    result = client.analyse_incident(
        "Mock title",
        "Mock description",
    )

    assert result == {
        "recommended_status": "Active",
        "classification": "Undetermined",
        "comment": "Mock benchmark result.",
    }
