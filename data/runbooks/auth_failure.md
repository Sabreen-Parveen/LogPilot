# Runbook: Authentication / authorization failure
**Category:** auth_failure
## Symptoms
401 Unauthorized, 403 Forbidden, "denied: denied", ExpiredToken, "authentication required", missing token scope.
## Diagnosis
1. Which endpoint: container registry, package registry, cloud API?
2. Token expired, rotated, or missing a scope (e.g. read:packages). PRs from forks lack secrets.
## Fix
Rotate the token, grant the scope, or switch to OIDC federation for cloud credentials.
