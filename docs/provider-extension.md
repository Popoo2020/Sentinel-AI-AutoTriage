# Provider Extension Boundary

Sentinel-AI-AutoTriage now exposes a small completion-provider boundary so the
rest of the security workflow does not need to change when the source of model
text changes.

## Why this exists

The triage pipeline contains several controls that should remain stable regardless
of model-provider choice:

- pre-LLM redaction,
- strict response parsing,
- deterministic recommendation policy,
- human approval requirements,
- metadata-only decision logging.

A provider adapter should supply **raw completion text only**.  The safety pipeline
around that text remains inside the repository.

## Current provider primitives

The repository includes:

```text
src/providers.py
```

with:

- `CompletionProvider` — the minimal protocol expected by `LLMClient`,
- `StaticMockProvider` — a deterministic provider for tests and benchmark runs.

The repository also includes:

```text
src/azure_provider.py
```

as an explicit extension-point scaffold for attaching an enterprise-hosted model
provider in a future implementation.

## Minimal provider contract

A provider only needs to implement:

```python
def complete(
    *,
    prompt: str,
    model_name: str,
    temperature: float,
    max_tokens: int,
) -> str:
    ...
```

The returned string is then parsed and validated by `LLMClient`.

## Example: deterministic local provider

```python
from src.llm_client import LLMClient
from src.providers import StaticMockProvider

client = LLMClient(
    model_name="benchmark-mock",
    provider=StaticMockProvider(
        '{"recommended_status":"Active","classification":"Undetermined","comment":"Mock provider output."}'
    ),
)

result = client.analyse_incident(
    "Example title",
    "Example description",
)
```

## Enterprise-provider extension guidance

A future enterprise-hosted adapter should:

1. accept configuration through environment variables or a secure runtime secret source,
2. avoid leaking provider-specific credentials into logs,
3. return only raw model text to the `LLMClient`,
4. leave redaction, parsing, policy and approval decisions unchanged,
5. be covered by adapter-specific tests and environment validation.

## What this does not imply

This scaffold does **not** claim that every provider is already fully implemented.
The current portfolio baseline demonstrates a clean provider boundary, deterministic
mock evaluation, and a documented extension path for a managed enterprise model
integration.
