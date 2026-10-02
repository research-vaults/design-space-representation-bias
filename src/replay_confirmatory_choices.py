#!/usr/bin/env python3
"""Independent replay of confirmatory choice and discovery quantities."""

from itertools import combinations

import numpy as np

from common import DATA, load_json, total_variation, write_output

HERE = DATA / "confirmatory_choices"
EXPECTED = load_json(DATA / "expected_results.json")["confirmatory_choices"]
SAMPLE_COUNTS = [1, 2, 3, 4, 6, 8, 12, 16, 24]


def load_cells():
    cells = {}
    for path in sorted(HERE.glob("lp_*.json")) + sorted(HERE.glob("local_*.json")):
        for rec in load_json(path).values():
            cells[(rec["model"], rec["landscape"], rec["arm"])] = rec
    return cells


def discovery_auc(probabilities: dict, utilities: dict) -> float:
    items = sorted(utilities.items(), key=lambda item: item[1])
    scale = sum(probabilities.values()) or 1.0
    probs = [probabilities.get(name, 0.0) / scale for name, _ in items]
    values = [value for _, value in items]
    lo, hi = values[0], values[-1]
    cumulative = 0.0
    cdf = []
    for probability in probs:
        cumulative += probability
        cdf.append(cumulative)
    curve = []
    for n in SAMPLE_COUNTS:
        expectation = 0.0
        previous = 0.0
        for value, fraction in zip(values, cdf):
            expectation += value * (fraction**n - previous**n)
            previous = fraction
        curve.append((expectation - lo) / (hi - lo))
    area = sum(
        0.5 * (curve[i] + curve[i + 1]) * (SAMPLE_COUNTS[i + 1] - SAMPLE_COUNTS[i])
        for i in range(len(SAMPLE_COUNTS) - 1)
    )
    return area / (SAMPLE_COUNTS[-1] - SAMPLE_COUNTS[0])


def main() -> int:
    cells = load_cells()
    utility_records = load_json(HERE / "utilities.json")
    landscapes = list(utility_records)
    models = sorted(EXPECTED["replicate_floor"])
    failures = []
    checks = 0

    no_op_class = {
        landscape: next(name for name, rec in utility_records[landscape]["classes"].items() if "default" in rec["members"])
        for landscape in landscapes
    }

    for model in models:
        floors = []
        for landscape in landscapes:
            a = cells.get((model, landscape, "canon"))
            b = cells.get((model, landscape, "canon_replicate"))
            if a and b:
                floors.append(total_variation(a["class_prob"], b["class_prob"]))
        observed = float(np.mean(floors))
        expected = EXPECTED["replicate_floor"][model]
        checks += 1
        if abs(observed - expected) > 1e-4:
            failures.append(f"replicate floor {model}: {observed} != {expected}")

        for arm in ("canon", "raw"):
            values = [
                cells[(model, landscape, arm)]["class_prob"].get(no_op_class[landscape], 0.0)
                for landscape in landscapes if (model, landscape, arm) in cells
            ]
            observed = float(np.mean(values))
            expected = EXPECTED["noop"][model][arm]
            checks += 1
            if abs(observed - expected) > 1e-4:
                failures.append(f"no-op {model}/{arm}: {observed} != {expected}")

        auc_differences = []
        for landscape in landscapes:
            canonical = cells.get((model, landscape, "canon"))
            raw = cells.get((model, landscape, "raw"))
            if not canonical or not raw:
                continue
            utilities = {name: rec["u"] for name, rec in utility_records[landscape]["classes"].items()}
            auc_differences.append(discovery_auc(canonical["class_prob"], utilities) - discovery_auc(raw["class_prob"], utilities))
        observed = float(np.mean(auc_differences))
        expected = EXPECTED["auc_canonical_minus_raw"][model]
        checks += 1
        if abs(observed - expected) > 1e-4:
            failures.append(f"canonical-minus-raw AUC {model}: {observed} != {expected}")

        ensemble_differences = []
        for landscape in landscapes:
            utilities = {name: rec["u"] for name, rec in utility_records[landscape]["classes"].items()}
            replicates = [
                cells[(model, landscape, f"rep_{index}")]
                for index in range(8)
                if (model, landscape, f"rep_{index}") in cells
                and cells[(model, landscape, f"rep_{index}")]["captured_mass"] >= 0.90
            ]
            if len(replicates) < 5:
                continue
            singles = [discovery_auc(rec["class_prob"], utilities) for rec in replicates]
            mixed = []
            for subset in combinations(range(len(replicates)), 4):
                distribution = {
                    name: sum(replicates[index]["class_prob"].get(name, 0.0) for index in subset) / 4
                    for name in utilities
                }
                mixed.append(discovery_auc(distribution, utilities))
            ensemble_differences.append(float(np.mean(mixed)) - float(np.mean(singles)))
        observed = float(np.mean(ensemble_differences))
        expected = EXPECTED["ensemble_minus_mean_single"][model]
        checks += 1
        if abs(observed - expected) > 1e-4:
            failures.append(f"ensemble contrast {model}: {observed} != {expected}")

    if len(cells) != EXPECTED["cells"]:
        failures.append(f"cell count {len(cells)} != {EXPECTED['cells']}")
    if checks != EXPECTED["checks"]:
        failures.append(f"check count {checks} != {EXPECTED['checks']}")

    report = {"cells": len(cells), "checks": checks, "failures": failures, "status": "PASS" if not failures else "FAIL"}
    write_output("confirmatory_choices.json", report)
    print(f"confirmatory choices: {report['status']} — {len(cells)} cells, {checks} checks")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
