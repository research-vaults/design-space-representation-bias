from __future__ import annotations

import math

import numpy as np

MODELS = ["Qwen/Qwen2.5-0.5B-Instruct", "Qwen/Qwen2.5-1.5B-Instruct"]
FAMILIES = ["uncorrelated", "weakly_correlated", "strongly_correlated", "inverse_correlated", "spanner", "clustered_profit"]


def greedy(instance: dict, policy: str) -> tuple[int, ...]:
    weights = np.asarray(instance["weights"])
    values = np.asarray(instance["values"])
    if policy == "density":
        order = sorted(range(len(weights)), key=lambda i: (-values[i] / weights[i], -values[i], weights[i], i))
    elif policy == "value":
        order = sorted(range(len(weights)), key=lambda i: (-values[i], weights[i], i))
    elif policy == "light":
        order = sorted(range(len(weights)), key=lambda i: (weights[i], -values[i], i))
    elif policy == "balanced":
        order = sorted(range(len(weights)), key=lambda i: (-values[i] / math.sqrt(weights[i]), -values[i], weights[i], i))
    elif policy == "steep_density":
        order = sorted(range(len(weights)), key=lambda i: (-values[i] / (weights[i] ** 1.5), -values[i], weights[i], i))
    else:
        raise ValueError(policy)
    chosen, used = [], 0
    for index in order:
        if used + int(weights[index]) <= instance["capacity"]:
            chosen.append(index)
            used += int(weights[index])
    return tuple(sorted(chosen))


def value_of(instance: dict, chosen: tuple[int, ...]) -> int:
    return int(sum(instance["values"][index] for index in chosen))


def best_one_swap(instance: dict, chosen: tuple[int, ...]) -> tuple[int, ...]:
    selected = set(chosen)
    weights, values = instance["weights"], instance["values"]
    used = sum(weights[index] for index in selected)
    best = (0, 0, 0)
    for outgoing in sorted(selected):
        for incoming in range(len(weights)):
            if incoming in selected:
                continue
            if used - weights[outgoing] + weights[incoming] <= instance["capacity"]:
                best = max(best, (values[incoming] - values[outgoing], -incoming, -outgoing))
    if best[0] <= 0:
        return tuple(sorted(selected))
    incoming, outgoing = -best[1], -best[2]
    selected.remove(outgoing)
    selected.add(incoming)
    return tuple(sorted(selected))


def run_policy(policy: str, instance: dict) -> tuple[int, ...]:
    if policy in {"density", "value", "light", "balanced", "steep_density"}:
        return greedy(instance, policy)
    if policy.endswith("_swap"):
        return best_one_swap(instance, greedy(instance, policy.removesuffix("_swap")))
    if policy == "portfolio":
        left = best_one_swap(instance, greedy(instance, "density"))
        right = greedy(instance, "value")
        return left if (value_of(instance, left), tuple(-i for i in left)) >= (value_of(instance, right), tuple(-i for i in right)) else right
    raise ValueError(policy)


def expected_utility(probabilities: dict, family: str, utilities: dict) -> float:
    return sum(float(probability) * utilities["families"][family]["policies"][policy]["mean_ratio"] for policy, probability in probabilities.items())
