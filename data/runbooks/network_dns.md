# Runbook: Network / DNS failure
**Category:** network_dns
## Symptoms
UnknownHostException, "Name or service not known", gaierror, "Could not resolve host", "Connection refused".
## Diagnosis
1. Wrong hostname (service container alias vs localhost)?
2. Service container not yet listening (connection refused) — different from a timeout.
3. Real outage of an external registry.
## Fix
Fix the host alias in the workflow `services:` block; wait on healthcheck; add a mirror for external registries.
