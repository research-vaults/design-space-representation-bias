from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_output(name: str, payload) -> None:
    OUTPUTS.mkdir(exist_ok=True)
    (OUTPUTS / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def total_variation(p: dict, q: dict) -> float:
    keys = set(p) | set(q)
    sp = sum(p.values()) or 1.0
    sq = sum(q.values()) or 1.0
    return 0.5 * sum(abs(p.get(k, 0.0) / sp - q.get(k, 0.0) / sq) for k in keys)
