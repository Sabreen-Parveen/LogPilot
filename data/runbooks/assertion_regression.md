# Runbook: Assertion failure from a real regression
**Category:** assertion_regression
## Symptoms
AssertionFailedError expected X but was Y; assert status_code == 200 got 500; fails consistently on every retry.
## Diagnosis
1. Deterministic (fails 3/3) → real behaviour change, not flakiness.
2. Correlate with the commit range: git log / git blame on the code under test.
## Fix
Fix the bug or, if behaviour change is intended, update the test in the same PR with justification. Never quarantine a deterministic failure.
