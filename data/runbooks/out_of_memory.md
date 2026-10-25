# Runbook: Out of memory during build/test
**Category:** out_of_memory
## Symptoms
java.lang.OutOfMemoryError, "JavaScript heap out of memory", MemoryError, exit code 137, OOMKilled, "Killed: 9".
## Diagnosis
1. Exit code 137 = SIGKILL from the kernel/cgroup, almost always memory.
2. Check parallelism (pytest-xdist workers, Gradle maxParallelForks) vs runner RAM.
3. Look for unbounded collections in fixtures or loading entire datasets in tests.
## Fix
Set -Xmx / NODE_OPTIONS=--max-old-space-size explicitly; reduce workers; raise container limit; fix the leak.
