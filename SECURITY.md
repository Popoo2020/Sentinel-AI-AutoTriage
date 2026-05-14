# Security Notes

Sentinel-AI-AutoTriage is a security-focused prototype for **authorised** Microsoft Sentinel triage experiments.  It is not intended for unattended production incident closure without additional governance, validation and operational review.

## Safe operating model

- The default operating mode is **dry-run**.
- `AUTO_APPLY_CHANGES=false` should remain the default unless testing in a controlled environment.
- Any write action to Sentinel should be reviewed within the organisation's incident-response and change-management procedures.
- Model output is treated as a **recommendation**, not as an independent authority.

## Data minimisation before LLM invocation

The project includes a deterministic redaction layer that masks representative:

- secret-like key/token values,
- password-like values,
- bearer tokens,
- email addresses,
- IPv4 addresses.

This is a transparent portfolio-grade example of data minimisation.  It is **not** a complete DLP system and should not be treated as a substitute for enterprise data classification, secret scanning or privacy controls.

## Responsible use

Use the project only with:

- workspaces and incidents you are authorised to access,
- test data or operational environments approved for such automation,
- appropriate Azure permissions based on least privilege.

## Reporting issues

Security-relevant defects should be handled responsibly.  When reporting an issue, include:

- the affected file or workflow,
- the observed behaviour,
- why it could affect safe operation,
- a minimal reproducible example when possible.
