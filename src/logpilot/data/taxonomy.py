"""Closed set of root-cause categories.

Every component (synthetic generator, RAG corpus, agent output schema, ML baseline,
eval metrics) keys off this list, so it is the single source of truth.
"""
from __future__ import annotations

from enum import Enum


class RootCause(str, Enum):
    DEPENDENCY_TIMEOUT = "dependency_timeout"      # downstream service / DB too slow
    OUT_OF_MEMORY = "out_of_memory"                # JVM heap / container OOMKilled
    NULL_REFERENCE = "null_reference"              # NPE / AttributeError on None
    FLAKY_RACE = "flaky_race"                      # order/timing-dependent test
    MISSING_CONFIG = "missing_config"              # env var / secret / property absent
    DISK_FULL = "disk_full"                        # no space left on runner
    AUTH_FAILURE = "auth_failure"                  # expired token, 401/403 to registry/API
    NETWORK_DNS = "network_dns"                    # name resolution / connection refused
    ASSERTION_REGRESSION = "assertion_regression"  # real behaviour change caught by a test
    DEPENDENCY_CONFLICT = "dependency_conflict"    # version clash, missing class/module


CATEGORIES: list[str] = [c.value for c in RootCause]

DESCRIPTIONS: dict[str, str] = {
    "dependency_timeout": "A call to a downstream dependency (DB, HTTP service, queue) exceeded its timeout.",
    "out_of_memory": "The process or container ran out of memory (heap exhausted, OOMKilled, exit 137).",
    "null_reference": "Code dereferenced a null/None value (NullPointerException, AttributeError on NoneType).",
    "flaky_race": "Non-deterministic failure from timing, ordering, or shared state between tests; passes on retry.",
    "missing_config": "A required environment variable, secret, or configuration property was not set.",
    "disk_full": "The build machine or container ran out of disk space.",
    "auth_failure": "Credentials were missing, expired, or lacked permission (401/403, expired token).",
    "network_dns": "Hostname could not be resolved or the connection was refused/unreachable.",
    "assertion_regression": "A test assertion failed because application behaviour changed (genuine bug).",
    "dependency_conflict": "Incompatible library versions or a missing class/module at build or runtime.",
}
