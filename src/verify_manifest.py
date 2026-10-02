#!/usr/bin/env python3
"""Verify the release files against MANIFEST.sha256."""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"


def main() -> int:
    failures = []
    entries = 0
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        path = ROOT / relative
        entries += 1
        if not path.is_file():
            failures.append(f"missing: {relative}")
            continue
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != digest:
            failures.append(f"hash mismatch: {relative}")
    print(f"manifest: {'PASS' if not failures else 'FAIL'} — {entries} files")
    for failure in failures:
        print(f"  {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
