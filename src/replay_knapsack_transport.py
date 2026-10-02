#!/usr/bin/env python3
"""Independent executable and numerical audit of the knapsack transport experiment."""

import hashlib
import json
import statistics as stats

from common import DATA, load_json, total_variation, write_output
from knapsack_core import FAMILIES, MODELS, expected_utility, run_policy

HERE = DATA / "knapsack_transport"
EXPECTED = load_json(DATA / "expected_results.json")["knapsack_transport"]


def main() -> int:
    benchmark = load_json(HERE / "base" / "benchmark.json")
    spaces = load_json(HERE / "base" / "spaces.json")
    utilities = load_json(HERE / "base" / "utilities.json")
    base_results = load_json(HERE / "base" / "results_raw.json")
    permutation_spec = load_json(HERE / "permutations" / "permutations.json")["permutations"]
    permutation_results = load_json(HERE / "permutations" / "results_raw.json")
    policies = spaces["policies"]

    signatures = {}
    for policy in policies:
        executions = []
        for family in FAMILIES:
            for instance in benchmark["families"][family]["probe"]:
                executions.append(run_policy(policy, instance))
        signatures[policy] = hashlib.sha256((json.dumps(executions, sort_keys=True) + "\n").encode()).hexdigest()
    distinct_classes = len(set(signatures.values()))
    written_spaces_valid = all(set(entry["class_id"] for entry in entries) == set(policies) for entries in spaces["arms"].values())
    permutations_valid = (
        len(permutation_spec) == EXPECTED["permutations"]
        and len({tuple(item["permutation"]) for item in permutation_spec}) == EXPECTED["permutations"]
        and all(sorted(item["permutation"]) == list(range(len(policies))) for item in permutation_spec)
    )

    max_probability_error = 0.0
    max_aggregation_error = 0.0
    for is_permutation, raw in [(False, base_results), (True, permutation_results)]:
        for key, cell in raw["cells"].items():
            entry_prob, class_prob = cell["entry_prob"], cell["class_prob"]
            max_probability_error = max(max_probability_error, abs(sum(entry_prob.values()) - 1.0), abs(sum(class_prob.values()) - 1.0))
            if is_permutation:
                index = int(key.rsplit("|p", 1)[1])
                entries = [spaces["arms"]["canonical"][position] for position in permutation_spec[index]["permutation"]]
            else:
                arm = key.split("|")[-1]
                entries = spaces["arms"]["canonical" if arm == "canonical_replicate" else arm]
            mapping = {entry["entry_id"]: entry["class_id"] for entry in entries}
            aggregated = {policy: 0.0 for policy in policies}
            for entry, probability in entry_prob.items():
                aggregated[mapping[entry]] += probability
            max_aggregation_error = max(max_aggregation_error, max(abs(aggregated[policy] - class_prob.get(policy, 0.0)) for policy in policies))

    rows = []
    for model in MODELS:
        for family in FAMILIES:
            canonical = base_results["cells"][f"{model}|{family}|canonical"]["class_prob"]
            distances, utilities_seen, top_classes = [], [], []
            for item in permutation_spec:
                cell = permutation_results["cells"][f"{model}|{family}|p{item['index']:02d}"]
                distances.append(total_variation(canonical, cell["class_prob"]))
                utilities_seen.append(expected_utility(cell["class_prob"], family, utilities))
                top_classes.append(cell["top_class"])
            rows.append({
                "model": model, "family": family, "median_tv": stats.median(distances),
                "top_class_count": len(set(top_classes)), "utility_range": max(utilities_seen) - min(utilities_seen),
            })

    summary = {}
    for model in MODELS:
        model_rows = [row for row in rows if row["model"] == model]
        family_medians = [row["median_tv"] for row in model_rows]
        summary[model] = {
            "median_tv": stats.median(family_medians),
            "families_above_threshold": sum(value > 0.05 for value in family_medians),
            "leave_one_family_out_minimum": min(stats.median([value for j, value in enumerate(family_medians) if j != i]) for i in range(len(family_medians))),
            "families_with_four_top_classes": sum(row["top_class_count"] >= 4 for row in model_rows),
            "families_with_utility_range": sum(row["utility_range"] > 0.005 for row in model_rows),
        }
    stronger = max(MODELS, key=lambda model: summary[model]["median_tv"])
    criteria = {
        "executable_classes_distinct": distinct_classes == EXPECTED["executable_classes"] and written_spaces_valid and permutations_valid,
        "both_model_medians_above_threshold": all(summary[model]["median_tv"] > 0.05 for model in MODELS),
        "both_models_above_threshold_on_five_families": all(summary[model]["families_above_threshold"] >= 5 for model in MODELS),
        "stronger_model_robust_to_family_removal": summary[stronger]["leave_one_family_out_minimum"] > 0.05,
        "top_class_diversity": any(summary[model]["families_with_four_top_classes"] >= 3 for model in MODELS),
        "utility_consequence": any(summary[model]["families_with_utility_range"] >= 3 for model in MODELS),
    }

    failures = []
    if max_probability_error >= 1e-6 or max_aggregation_error >= 1e-6:
        failures.append("probability or entry-to-class aggregation error")
    if not all(criteria.values()):
        failures.append("one or more transport criteria failed")
    for model, expected in EXPECTED["models"].items():
        for key in ("median_tv", "families_above_threshold", "families_with_four_top_classes", "families_with_utility_range"):
            if abs(summary[model][key] - expected[key]) > 1e-6:
                failures.append(f"summary mismatch: {model}/{key}")

    report = {
        "executable_classes": distinct_classes, "written_spaces_valid": written_spaces_valid,
        "permutations_valid": permutations_valid, "probability_max_error": max_probability_error,
        "aggregation_max_error": max_aggregation_error, "summary": summary, "criteria": criteria,
        "failures": failures, "status": "PASS" if not failures else "FAIL",
    }
    write_output("knapsack_transport.json", report)
    print(f"knapsack transport: {report['status']} — {distinct_classes} classes, {len(permutation_spec)} permutations")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
