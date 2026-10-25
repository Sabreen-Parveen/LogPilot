# Runbook: Null / None dereference
**Category:** null_reference
## Symptoms
NullPointerException, KotlinNullPointerException, AttributeError: 'NoneType' object has no attribute, TypeError: Cannot read properties of undefined.
## Diagnosis
1. Top application frame in the stack trace (com.acme.* / src/*) is where the null was used, not necessarily where it came from.
2. Check whether test fixtures or a recent schema change left the field unset.
## Fix
Validate inputs at the boundary; use Optional/nullable types properly; fix the fixture. Distinguish from a DEBUG log saying a field is null (benign).
