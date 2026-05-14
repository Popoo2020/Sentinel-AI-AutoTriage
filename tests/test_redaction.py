from src.redaction import redact_text


def test_redact_text_masks_secret_like_values() -> None:
    result = redact_text(
        "api_key=sk-test-123 password=hunter2 Bearer abc.def.ghi"
    )

    assert "sk-test-123" not in result.text
    assert "hunter2" not in result.text
    assert "abc.def.ghi" not in result.text
    assert "[REDACTED_SECRET]" in result.text
    assert "[REDACTED_PASSWORD]" in result.text
    assert "Bearer [REDACTED_TOKEN]" in result.text
    assert result.redaction_count == 3
    assert result.redaction_types == ("api_key", "password", "bearer_token")


def test_redact_text_masks_email_and_ipv4() -> None:
    result = redact_text(
        "Alert for analyst@example.com from 10.20.30.40 requires review."
    )

    assert "analyst@example.com" not in result.text
    assert "10.20.30.40" not in result.text
    assert "[REDACTED_EMAIL]" in result.text
    assert "[REDACTED_IP]" in result.text
    assert result.redaction_count == 2


def test_redact_text_is_stable_for_benign_input() -> None:
    result = redact_text("Suspicious login pattern detected for a privileged role.")

    assert result.text == "Suspicious login pattern detected for a privileged role."
    assert result.redaction_count == 0
    assert result.redaction_types == ()
