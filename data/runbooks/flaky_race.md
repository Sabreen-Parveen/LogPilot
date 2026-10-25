# Runbook: Flaky / race-condition tests
**Category:** flaky_race
## Symptoms
Test fails then PASSES on rerun; ConcurrentModificationException; "event not received within Nms"; test on quarantine list.
## Diagnosis
1. Key signal: same commit, same test, passes on retry. Deterministic failures are NOT flaky.
2. Look for sleeps, shared DB state, test ordering assumptions, parallel workers.
## Fix
Replace sleeps with polling/awaitility; isolate state per test; quarantine and file a ticket. Do not just add retries.
