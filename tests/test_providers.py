from __future__ import annotations

from src.providers import StaticMockProvider


def test_static_mock_provider_returns_configured_response() -> None:
    provider = StaticMockProvider("mock-response")

    result = provider.complete(
        prompt="ignored prompt",
        model_name="mock-model",
        temperature=0.0,
        max_tokens=42,
    )

    assert result == "mock-response"
