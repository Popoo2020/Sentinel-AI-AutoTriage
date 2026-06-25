import json


def parse_llm_output(text: str):
    """Simple parser smoke helper for validating JSON handling examples."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def test_parse_valid_json():
    input_text = '{"incident_id": "123", "severity": "high"}'
    result = parse_llm_output(input_text)
    assert isinstance(result, dict)
    assert result["incident_id"] == "123"


def test_parse_invalid_json():
    input_text = "This is not JSON"
    result = parse_llm_output(input_text)
    assert result == {}
