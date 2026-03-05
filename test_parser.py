import json
import pytest


def parse_llm_output(text: str):
    """Simple parser that attempts to load JSON from LLM output."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def test_parse_valid_json():
    """Parser should return dict for valid JSON string."""
    input_text = '{"incident_id": "123", "severity": "high"}'
    result = parse_llm_output(input_text)
    assert isinstance(result, dict)
    assert result["incident_id"] == "123"


def test_parse_invalid_json():
    """Parser should return empty dict for malformed JSON."""
    input_text = 'This is not JSON'
    result = parse_llm_output(input_text)
    assert result == {}