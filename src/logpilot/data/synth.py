"""Synthetic labelled CI/test failure logs.

Each generated case is a realistic-looking CI log: setup noise, build/test output, one or
more *signal* lines that reveal the true root cause, and (in hard mode) *red herrings* —
lines that look like a different category but are not what failed the build.

Splits are produced from disjoint seeds and disjoint template variants where possible,
so the RAG index (incidents) never contains the exact text an eval case was built from.
"""
from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

from logpilot.data.taxonomy import CATEGORIES

SERVICES = ["payments-api", "orders-svc", "user-profile", "inventory", "search-indexer", "notifications"]
HOSTS = ["db-primary.internal", "redis-cache.internal", "kafka-0.internal", "auth.internal", "s3.amazonaws.com"]
CLASSES = ["OrderService", "PaymentProcessor", "UserRepository", "CartController", "InventoryClient"]
TESTS = ["testCheckoutFlow", "test_refund_partial", "testConcurrentUpdates", "test_search_ranking", "testLoginRedirect"]
ENV_VARS = ["DATABASE_URL", "STRIPE_API_KEY", "AWS_REGION", "JWT_SECRET", "KAFKA_BOOTSTRAP_SERVERS"]
LIBS = [("jackson-databind", "2.15.2", "2.12.7"), ("protobuf", "4.25.1", "3.20.3"),
        ("netty-handler", "4.1.100", "4.1.68"), ("pydantic", "2.6.1", "1.10.13")]

# Signal templates: per category, a list of variants; each variant is a list of lines.
# Variants are split between incidents (even index) and eval (odd index) to limit leakage.
SIGNALS: dict[str, list[list[str]]] = {
    "dependency_timeout": [
        ["ERROR {cls} - Query timed out after 30000ms against {host}",
         "java.sql.SQLTimeoutException: Statement cancelled due to timeout or client request"],
        ["E   requests.exceptions.ReadTimeout: HTTPConnectionPool(host='{host}', port=443): Read timed out. (read timeout=10)"],
        ["io.grpc.StatusRuntimeException: DEADLINE_EXCEEDED: deadline exceeded after 4.99s calling {svc}"],
        ["E   asyncio.exceptions.TimeoutError", "E   during handling: redis.exceptions.TimeoutError: Timeout reading from redis-cache.internal:6379"],
    ],
    "out_of_memory": [
        ["java.lang.OutOfMemoryError: Java heap space", "\tat java.util.Arrays.copyOf(Arrays.java:3236)"],
        ["Error: Process completed with exit code 137.", "Container {svc}-test was OOMKilled (memory limit 2Gi)"],
        ["FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory"],
        ["E   MemoryError", "Killed: 9 (pytest worker gw2 exceeded memory limit)"],
    ],
    "null_reference": [
        ["java.lang.NullPointerException: Cannot invoke \"String.length()\" because \"customer.email\" is null",
         "\tat com.acme.{cls}.validate({cls}.java:88)"],
        ["E   AttributeError: 'NoneType' object has no attribute 'items'", "src/{svc}/handlers.py:142: AttributeError"],
        ["kotlin.KotlinNullPointerException", "\tat com.acme.{cls}.resolve({cls}.kt:51)"],
        ["TypeError: Cannot read properties of undefined (reading 'id')", "    at {cls}.render ({cls}.tsx:34:19)"],
    ],
    "flaky_race": [
        ["FAILED tests/test_{svc}.py::{test} - AssertionError: expected 2 rows, got 1",
         "Rerun 1/2 of {test}: PASSED", "Test marked FLAKY: passed on retry"],
        ["{test} FAILED: ConcurrentModificationException at java.util.ArrayList$Itr.checkForComodification",
         "Retrying failed tests (attempt 2)... {test} PASSED"],
        ["E   AssertionError: event not received within 500ms (ordering not guaranteed)",
         "[gw3] PASSED on rerun tests/test_events.py::{test}"],
        ["Condition not satisfied: eventually {{ cache.size() == 3 }} after 1000ms",
         "Test {test} is known-flaky (quarantine list), passed on retry 2"],
    ],
    "missing_config": [
        ["Caused by: java.lang.IllegalArgumentException: Could not resolve placeholder '{env}' in value \"${{{env}}}\""],
        ["E   KeyError: '{env}'", "src/{svc}/settings.py:12: KeyError"],
        ["pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings",
         "{env_lower}\n  Field required [type=missing]"],
        ["Error: Required environment variable {env} is not set", "##[error]Process completed with exit code 1."],
    ],
    "disk_full": [
        ["java.io.IOException: No space left on device", "\tat java.io.FileOutputStream.writeBytes(Native Method)"],
        ["OSError: [Errno 28] No space left on device: '/tmp/pytest-of-runner/'"],
        ["failed to register layer: write /var/lib/docker/overlay2/...: no space left on device"],
        ["System.IO.IOException: There is not enough space on the disk.", "Runner disk usage: 100% of 14GB"],
    ],
    "auth_failure": [
        ["Error response from daemon: Get https://ghcr.io/v2/: denied: denied", "unauthorized: authentication required"],
        ["botocore.exceptions.ClientError: An error occurred (ExpiredToken) when calling the GetObject operation: The security token included in the request is expired"],
        ["Could not GET 'https://maven.pkg.github.com/acme/{svc}': Received status code 401 from server: Unauthorized"],
        ["HTTP 403 Forbidden from {host}: token lacks scope 'read:packages'"],
    ],
    "network_dns": [
        ["java.net.UnknownHostException: {host}: Name or service not known"],
        ["E   socket.gaierror: [Errno -3] Temporary failure in name resolution"],
        ["Caused by: java.net.ConnectException: Connection refused: {host}/10.0.3.17:5432"],
        ["curl: (6) Could not resolve host: {host}", "##[error]Process completed with exit code 6."],
    ],
    "assertion_regression": [
        ["org.opentest4j.AssertionFailedError: expected: <1050> but was: <1000>",
         "\tat com.acme.{cls}Test.{test}({cls}Test.java:73)", "Test {test} FAILED (also failed on retry)"],
        ["E   assert response.status_code == 200", "E    +  where 500 = <Response [500]>.status_code",
         "FAILED tests/test_{svc}.py::{test} (deterministic: failed 3/3 runs)"],
        ["Expected: \"order_confirmed\"\n     but: was \"order_pending\"", "{test} FAILED after commit a1b2c3d changed status logic"],
        ["E   AssertionError: assert 0.15 == 0.2", "E    discount rate changed in pricing.py (git blame: 2 hours ago)"],
    ],
    "dependency_conflict": [
        ["java.lang.NoSuchMethodError: 'com.fasterxml.jackson.core.JsonParser com.fasterxml.jackson.databind.ObjectMapper.createParser'",
         "Dependency convergence error for {lib}:{v1} paths to dependency are: {lib}:{v2}"],
        ["E   ModuleNotFoundError: No module named 'pydantic.v1'"],
        ["ERROR: pip's dependency resolver: {lib} {v1} requires {lib}<{v2}, but you have {lib} {v1} which is incompatible."],
        ["java.lang.ClassNotFoundException: io.netty.handler.ssl.OpenSslContext", "Conflict: {lib} {v1} vs {v2} on classpath"],
    ],
}

# Plausible-but-irrelevant lines, keyed by the category they would *falsely* suggest.
RED_HERRINGS: dict[str, list[str]] = {
    "dependency_timeout": ["WARN  HikariPool-1 - Connection is slow to validate (1200ms), continuing"],
    "out_of_memory": ["WARN  GC overhead: young gen collection took 340ms"],
    "null_reference": ["DEBUG optional field 'middleName' is null, using default"],
    "flaky_race": ["INFO  Retrying flaky network fetch for cache warmup (attempt 2)... ok"],
    "missing_config": ["WARN  SENTRY_DSN not set, error reporting disabled"],
    "disk_full": ["WARN  Runner disk usage at 81%"],
    "auth_failure": ["WARN  Token for codecov expires in 3 days"],
    "network_dns": ["WARN  IPv6 lookup for registry.npmjs.org failed, falling back to IPv4"],
    "assertion_regression": ["INFO  Snapshot updated: 2 snapshots written"],
    "dependency_conflict": ["WARN  Deprecated API usage: kotlin.coroutines.experimental"],
}

SETUP_NOISE = [
    "##[group]Run actions/checkout@v4", "Syncing repository: acme/{svc}", "##[endgroup]",
    "##[group]Set up job", "Runner image: ubuntu-22.04 (20251012.1)", "##[endgroup]",
    "Downloading https://services.gradle.org/distributions/gradle-8.5-bin.zip",
    "Collecting pytest==8.1.1", "Successfully installed pytest-8.1.1 pytest-xdist-3.5.0",
    "> Task :compileKotlin", "> Task :processResources UP-TO-DATE",
    "INFO  Starting {svc} test context (profile=ci)", "INFO  Flyway: Successfully applied 14 migrations",
    "============================= test session starts ==============================",
    "collected 312 items", "tests/test_health.py ....                                [  1%]",
    "> Task :test", "{cls}Test > testHealthEndpoint() PASSED",
]
TAIL_NOISE = [
    "##[error]Process completed with exit code 1.", "BUILD FAILED in 3m 12s",
    "=========================== short test summary info ============================",
    "Post job cleanup.", "Uploading artifact test-results.xml",
]


@dataclass
class LogCase:
    id: str
    split: str
    root_cause: str
    service: str
    difficulty: str  # "easy" | "hard"
    log: str
    signal_lines: list[str] = field(default_factory=list)
    resolution: str = ""  # only meaningful for incidents (what fixed it)


RESOLUTIONS: dict[str, list[str]] = {
    "dependency_timeout": ["Raised client timeout and added index on slow query.", "Downstream {host} was degraded; added retry with backoff."],
    "out_of_memory": ["Increased -Xmx for test JVM and fixed unbounded list in fixture.", "Raised container memory limit; reduced pytest-xdist workers."],
    "null_reference": ["Added null check and validation at API boundary.", "Fixed fixture that left field unset."],
    "flaky_race": ["Replaced sleep with awaitility/polling; isolated shared DB state per test.", "Quarantined test, fixed ordering assumption."],
    "missing_config": ["Added {env} to CI secrets and to .env.example.", "Provided default in application-ci.yml."],
    "disk_full": ["Added docker system prune step; cleaned Gradle cache.", "Moved to larger runner."],
    "auth_failure": ["Rotated expired token in repo secrets.", "Granted read:packages scope to CI token."],
    "network_dns": ["Fixed hostname in CI service container config.", "Service container was not ready; added healthcheck wait."],
    "assertion_regression": ["Reverted offending commit; added test for edge case.", "Fixed pricing logic bug introduced in recent PR."],
    "dependency_conflict": ["Pinned {lib} to a single version via dependency constraints.", "Upgraded transitive dependency to compatible version."],
}


def _fill(template: str, rng: random.Random) -> str:
    lib, v1, v2 = rng.choice(LIBS)
    env = rng.choice(ENV_VARS)
    return template.format(
        svc=rng.choice(SERVICES), host=rng.choice(HOSTS), cls=rng.choice(CLASSES),
        test=rng.choice(TESTS), env=env, env_lower=env.lower(), lib=lib, v1=v1, v2=v2,
    )


def _ordered_sample(items: list[str], k: int, rng: random.Random) -> list[str]:
    """Random subset that keeps original order (real logs are chronological)."""
    return [items[i] for i in sorted(rng.sample(range(len(items)), k))]


def make_case(idx: int, split: str, category: str, rng: random.Random, hard: bool) -> LogCase:
    variants = SIGNALS[category]
    # incidents draw from even variants, dev/test from odd -> retrieval must generalise.
    pool = variants[0::2] if split == "incidents" else variants[1::2]
    signal = [_fill(line, rng) for line in rng.choice(pool)]

    lines = [_fill(line, rng) for line in _ordered_sample(SETUP_NOISE, rng.randint(8, len(SETUP_NOISE)), rng)]
    if hard:
        others = [c for c in CATEGORIES if c != category]
        for c in rng.sample(others, k=2):
            lines.insert(rng.randrange(len(lines)), _fill(rng.choice(RED_HERRINGS[c]), rng))
    insert_at = rng.randrange(len(lines) // 2, len(lines) + 1)
    lines[insert_at:insert_at] = signal
    lines += _ordered_sample(TAIL_NOISE, rng.randint(2, len(TAIL_NOISE)), rng)

    return LogCase(
        id=f"{split}-{idx:04d}", split=split, root_cause=category,
        service=rng.choice(SERVICES), difficulty="hard" if hard else "easy",
        log="\n".join(lines), signal_lines=signal,
        resolution=_fill(rng.choice(RESOLUTIONS[category]), rng) if split == "incidents" else "",
    )


SPLIT_SEEDS = {"incidents": 1, "dev": 2, "test": 3}


def generate_split(split: str, per_category: int, hard_ratio: float = 0.4) -> list[LogCase]:
    rng = random.Random(SPLIT_SEEDS[split])
    cases: list[LogCase] = []
    for category in CATEGORIES:
        for _ in range(per_category):
            cases.append(make_case(len(cases), split, category, rng, hard=rng.random() < hard_ratio))
    rng.shuffle(cases)
    return cases


def write_jsonl(cases: list[LogCase], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for c in cases:
            f.write(json.dumps(asdict(c)) + "\n")


def read_jsonl(path: Path) -> list[LogCase]:
    with path.open() as f:
        return [LogCase(**json.loads(line)) for line in f if line.strip()]


def main(out_dir: str = "data/synthetic") -> None:
    sizes = {"incidents": 8, "dev": 5, "test": 10}  # per category -> 80 / 50 / 100 cases
    for split, n in sizes.items():
        cases = generate_split(split, n)
        write_jsonl(cases, Path(out_dir) / f"{split}.jsonl")
        print(f"wrote {len(cases):>4} cases -> {out_dir}/{split}.jsonl")


if __name__ == "__main__":
    main()
