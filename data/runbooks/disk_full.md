# Runbook: Runner out of disk space
**Category:** disk_full
## Symptoms
"No space left on device", Errno 28, docker "failed to register layer", "not enough space on the disk".
## Diagnosis
Hosted runners have ~14GB free. Docker images, Gradle/npm caches, and test artifacts fill it.
## Fix
Add `docker system prune -af`, clean caches, remove unused toolchains, or use a larger runner. Disk at ~80% with a WARN is not itself a failure.
