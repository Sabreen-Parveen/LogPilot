# Runbook: Dependency timeout in CI
**Category:** dependency_timeout
## Symptoms
SQLTimeoutException, ReadTimeout, gRPC DEADLINE_EXCEEDED, redis TimeoutError; test fails after a fixed wait (5s/10s/30s).
## Diagnosis
1. Identify which host/service timed out from the exception message.
2. Check if the dependency is a CI service container (did it start? healthcheck?) or a real remote.
3. Look for slow queries (missing index after migration) or large fixtures.
## Fix
Add a healthcheck wait for service containers; raise timeout only if the call is legitimately slow; add retry with backoff for remote calls; mock external services in unit tests.
