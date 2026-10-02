#!/usr/bin/env python3
"""Recompute prompt-group sensitivity and empirical replicate floors."""

import itertools
from collections import defaultdict

import numpy as np

from common import DATA, load_json, total_variation, write_output

HERE = DATA / "sampled_choices"
EXPECTED = load_json(DATA / "prompt_group_expected.json")
RNG = np.random.default_rng(20260824)
BOOTSTRAP_SAMPLES = 4000
MIN_CALLS = 12


def cluster_interval(by_cluster: dict) -> tuple[float, float, float, int]:
    keys = sorted(by_cluster, key=str)
    means = np.asarray([np.mean(by_cluster[key]) for key in keys], dtype=float)
    estimate = float(means.mean())
    indices = RNG.integers(0, len(keys), size=(BOOTSTRAP_SAMPLES, len(keys)))
    samples = means[indices].mean(axis=1)
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return estimate, float(lo), float(hi), len(keys)


def main() -> int:
    groups = {landscape: group for group, landscapes in EXPECTED["groups"].items() for landscape in landscapes}
    cache = load_json(HERE / "llm_cache.json")
    calls = defaultdict(list)
    for key, record in cache.items():
        model, landscape, arm, _ = key.split("|")
        if record.get("class_id"):
            calls[(model, landscape, arm)].append(record["class_id"])

    arms = sorted({key[2] for key in calls} - {"canonical", "canonical_replicate"})
    failures = []
    observed_arms = {}
    for arm in arms:
        by_group = defaultdict(list)
        for model, landscape, current_arm in list(calls):
            if current_arm != arm:
                continue
            canonical = calls.get((model, landscape, "canonical"))
            alternative = calls.get((model, landscape, arm))
            if not canonical or not alternative or min(len(canonical), len(alternative)) < MIN_CALLS:
                continue
            p = {name: canonical.count(name) for name in set(canonical) | set(alternative)}
            q = {name: alternative.count(name) for name in set(canonical) | set(alternative)}
            by_group[groups[landscape]].append(total_variation(p, q))
        estimate, lo, hi, n = cluster_interval(by_group)
        observed_arms[arm] = {"est": estimate, "lo": lo, "hi": hi, "n": n}
        expected = EXPECTED["arms"][arm]["prompt_group"]
        if max(abs(estimate - expected["est"]), abs(lo - expected["lo"]), abs(hi - expected["hi"])) > 0.005:
            failures.append(f"prompt-group interval mismatch for {arm}")

    models = sorted({key[0] for key in calls})
    landscapes = sorted(groups)
    replicate_by_landscape = defaultdict(list)
    same_prompt_by_group = defaultdict(list)
    for model in models:
        for landscape in landscapes:
            a = calls.get((model, landscape, "canonical"))
            b = calls.get((model, landscape, "canonical_replicate"))
            if a and b and min(len(a), len(b)) >= MIN_CALLS:
                p = {name: a.count(name) for name in set(a) | set(b)}
                q = {name: b.count(name) for name in set(a) | set(b)}
                replicate_by_landscape[landscape].append(total_variation(p, q))
        for group in sorted(EXPECTED["groups"]):
            members = EXPECTED["groups"][group]
            for left, right in itertools.combinations(sorted(members), 2):
                a = calls.get((model, left, "canonical"))
                b = calls.get((model, right, "canonical"))
                if a and b and min(len(a), len(b)) >= MIN_CALLS:
                    p = {name: a.count(name) for name in set(a) | set(b)}
                    q = {name: b.count(name) for name in set(a) | set(b)}
                    same_prompt_by_group[group].append(total_variation(p, q))

    observed_floors = {}
    for label, values, expected_label in [
        ("same_batch", replicate_by_landscape, "declared replicate arm (same batch)"),
        ("identical_prompt_cross_time", same_prompt_by_group, "different landscapes, IDENTICAL prompt"),
    ]:
        estimate, lo, hi, n = cluster_interval(values)
        observed_floors[label] = {"est": estimate, "lo": lo, "hi": hi, "n": n}
        expected = EXPECTED["floors"][expected_label]
        if max(abs(estimate - expected["est"]), abs(lo - expected["lo"]), abs(hi - expected["hi"])) > 0.005:
            failures.append(f"replicate-floor mismatch for {label}")

    report = {"arms": observed_arms, "floors": observed_floors, "failures": failures, "status": "PASS" if not failures else "FAIL"}
    write_output("prompt_groups.json", report)
    print(f"prompt groups: {report['status']} — {len(observed_arms)} rewriting arms")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
