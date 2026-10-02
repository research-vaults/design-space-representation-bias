#!/usr/bin/env python3
"""Independent replay of the sampled protein-choice headline quantities."""

from collections import Counter, defaultdict

from common import DATA, load_json, total_variation, write_output

HERE = DATA / "sampled_choices"
EXPECTED = load_json(DATA / "expected_results.json")["sampled_choices"]


def main() -> int:
    cache = load_json(HERE / "llm_cache.json")
    quotient = load_json(HERE / "behavioural_quotient.json")
    spaces = load_json(HERE / "spaces.json")

    malformed = [k for k, v in cache.items() if not isinstance(v, dict) or "class_id" not in v or "entry" not in v]
    malformed_keys = [k for k in cache if len(k.split("|")) != 4]

    mismatches = []
    unchecked = 0
    per_arm = Counter()
    draws = defaultdict(list)
    for key, rec in cache.items():
        model, landscape, arm, _ = key.split("|")
        per_arm[(model, landscape, arm)] += 1
        if rec.get("class_id"):
            draws[(model, landscape, arm)].append(rec["class_id"])
        space_name = "canonical" if arm == "canonical_replicate" else arm
        menu = spaces.get(landscape, {}).get("spaces", {}).get(space_name)
        if not menu:
            unchecked += 1
            continue
        entry_to_class = {item["entry_id"]: item["class_id"] for item in menu}
        observed = entry_to_class.get(rec.get("entry"))
        if observed is None:
            unchecked += 1
        elif observed != rec.get("class_id"):
            mismatches.append((key, rec.get("entry"), rec.get("class_id"), observed))

    distributions = {}
    for (model, landscape, arm), values in draws.items():
        if landscape not in quotient:
            continue
        classes = [c["id"] for c in quotient[landscape]["classes"]]
        distributions[(model, landscape, arm)] = {c: values.count(c) / len(values) for c in classes}

    rewrites = {
        "order_permuted", "order_permuted_2", "order_permuted_3", "order_permuted_4",
        "order_permuted_5", "alias_expanded", "alias_expanded_shuffled", "dead_inflated",
        "blind_renamed", "verbosity_padded", "default_anchored",
    }
    by_landscape = defaultdict(list)
    for (model, landscape, arm), dist in distributions.items():
        if arm not in rewrites:
            continue
        canonical = distributions.get((model, landscape, "canonical"))
        replicate = distributions.get((model, landscape, "canonical_replicate"))
        if canonical and replicate:
            by_landscape[landscape].append(
                total_variation(canonical, dist) - total_variation(canonical, replicate)
            )
    landscape_means = [sum(v) / len(v) for v in by_landscape.values()]
    tv_excess = sum(landscape_means) / len(landscape_means)

    class_counts = sorted({rec["n_classes"] for rec in quotient.values()})
    largest = sorted({max((len(c["members"]) for c in rec["multi_member_classes"]), default=1) for rec in quotient.values()})
    call_counts = sorted(set(per_arm.values()))
    failures = []
    if len(cache) != EXPECTED["records"]:
        failures.append(f"record count {len(cache)} != {EXPECTED['records']}")
    if len(per_arm) != EXPECTED["arms"] or call_counts != [EXPECTED["calls_per_arm"]]:
        failures.append("per-arm call budget mismatch")
    if abs(tv_excess - EXPECTED["tv_excess"]) > 0.001:
        failures.append(f"TV excess {tv_excess:.6f} != {EXPECTED['tv_excess']:.6f}")
    if class_counts != EXPECTED["behaviour_class_counts"]:
        failures.append(f"class counts {class_counts} do not match")
    if largest != [EXPECTED["largest_class_size"]]:
        failures.append(f"largest class sizes {largest} do not match")
    if malformed or malformed_keys or mismatches:
        failures.append("schema or entry-to-class integrity failure")
    if unchecked != EXPECTED["unavailable_responses"]:
        failures.append(f"unavailable responses {unchecked} != {EXPECTED['unavailable_responses']}")

    report = {
        "records": len(cache), "malformed": len(malformed), "malformed_keys": len(malformed_keys),
        "entry_class_mismatches": len(mismatches), "unverifiable_entries": unchecked,
        "arms": len(per_arm), "calls_per_arm": call_counts, "tv_excess": tv_excess,
        "landscapes": len(landscape_means), "class_counts": class_counts,
        "largest_class_sizes": largest, "failures": failures, "status": "PASS" if not failures else "FAIL",
    }
    write_output("sampled_choices.json", report)
    print(f"sampled choices: {report['status']} — {len(cache)} records, TV excess {tv_excess:+.3f}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
