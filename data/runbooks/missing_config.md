# Runbook: Missing configuration or secret
**Category:** missing_config
## Symptoms
"Could not resolve placeholder", KeyError on an env var name, pydantic "Field required", "Required environment variable X is not set".
## Diagnosis
1. Name of the missing key is in the message.
2. Check CI secrets (forks do not receive secrets!), the workflow env block, and application-ci.yml.
## Fix
Add the secret/env var to CI; add a safe default for test profiles; document in .env.example. A WARN that an optional var (e.g. SENTRY_DSN) is unset is benign.
