"""Download Loghub 2k-line samples (https://github.com/logpai/loghub).

Loghub provides real system logs with per-line templates; the HDFS and BGL samples also
carry anomaly labels. We use them for:
  * the scikit-learn anomaly-detection baseline (Milestone 7), and
  * realistic background noise when stress-testing the parser.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/logpai/loghub/master"
SYSTEMS = ["HDFS", "BGL", "Hadoop", "Spark", "OpenStack", "Linux"]


def download(systems: list[str] = SYSTEMS, out_dir: str = "data/loghub") -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name in systems:
        for suffix in ("_2k.log", "_2k.log_structured.csv"):
            dest = out / f"{name}{suffix}"
            if dest.exists():
                continue
            url = f"{BASE}/{name}/{name}{suffix}"
            print(f"fetching {url}")
            urllib.request.urlretrieve(url, dest)


if __name__ == "__main__":
    download(sys.argv[1:] or SYSTEMS)
