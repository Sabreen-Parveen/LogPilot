# Runbook: Dependency version conflict
**Category:** dependency_conflict
## Symptoms
NoSuchMethodError, ClassNotFoundException, NoClassDefFoundError, ModuleNotFoundError, pip resolver incompatibility, Gradle "Dependency convergence error".
## Diagnosis
1. NoSuchMethodError at runtime = compiled against one version, running another.
2. Run `./gradlew dependencies` / `pip check` / `pipdeptree` to find the two paths.
## Fix
Pin via a BOM / dependency constraints / constraints.txt; upgrade the transitive dependency. A deprecation WARN is not a conflict.
