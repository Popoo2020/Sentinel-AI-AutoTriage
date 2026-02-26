def test_incident_summary_as_prompt():
    from src.models import IncidentSummary
    incident = IncidentSummary(
        id="1",
        title="Test Incident",
        description="This is a test incident",
        severity="High",
        status="Active",
    )
    assert incident.as_prompt() == "[High] Test Incident: This is a test incident"
