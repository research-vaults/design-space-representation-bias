# Same Algorithms, Different Scientist

Reproducibility package for *Same Algorithms, Different Scientist: Design Space Bias in AI Discovery*.

The study asks whether measured scientific credit changes when a policy menu is
rewritten without changing its executable opportunities. The executable behavioural
quotient groups written policies that produce the same query sets on fixed probes.
This release compares model choices over those behaviours rather than menu entries.

## Scope of this release

Snapshot: 2 October 2026. Four offline replay suites check sampled protein-policy
choices, confirmatory probability distributions, prompt-group sensitivity, and
transport to an executable synthetic knapsack problem. Frozen choices, class
mappings, utilities and expected numerical results are included. No model calls,
credentials, GPU, model downloads or raw biological tables are needed.

This is a public scientific artifact, not a certified anonymous review snapshot.
It is a bounded replay package, not a complete implementation of an autonomous
scientist or a reproduction of every analysis in the paper. Manuscripts and
unpublished working drafts are intentionally not bundled.

## Setup and reproduction

Use Python 3.11 or newer, with a version supported by the pinned NumPy dependency.
From a clean checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash reproduce.sh
```

Individual commands, from the repository root:

```bash
python src/verify_manifest.py
python src/replay_sampled_choices.py
python src/replay_confirmatory_choices.py
python src/replay_prompt_groups.py
python src/replay_knapsack_transport.py
```

Each command fails with a nonzero exit code on a failed check. Machine-readable
reports are written under `outputs/`; generated outputs are not committed.

## Inputs and expected outputs

All replay inputs are in `data/`. The sampled-choice data contain 8,088 scheduled
records, including 31 unavailable responses represented as null selections. The
suite checks 21–22 behavioural classes per protein landscape, a largest class of
19 written policies, and mean excess total variation of approximately 0.367 over
the replicate floor. This mean-excess statistic is not the paper's separately
reported median total variation.

The confirmatory replay checks 1,176 model/landscape/arm cells and 35 numerical
comparisons. The prompt-group replay respects shared prompt groups rather than
treating all 12 landscapes as independent prompts. The knapsack replay executes
eight policies, validates 24 permutations across six families, and checks six
transport criteria. Successful commands report PASS and zero failed checks.

Additional default-duplication results and constrained-choice records are retained
under `data/default_duplication/` for inspection. These newer records include
negative findings; the four replay suites do not reproduce that entire analysis.

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the measurement contracts and
[DATA_PROVENANCE.md](DATA_PROVENANCE.md) for provenance and distribution boundaries.
`MANIFEST.sha256` records all release files except itself.

## Included and excluded

Included: replay code, dependency pins, frozen study-generated numerical records,
written policy menus, synthetic knapsack inputs, numerical expectations and hashes.

Excluded: private reviews and correspondence, project-management records, author
identifiers, development histories, manuscripts, credentials, upstream biological
datasets, weights, caches and third-party source repositories. No personal
conversations or model reasoning traces are distributed. Model/provider names and
scientifically relevant revisions are retained for interpretability.

The existing MIT license is retained for this software and its documentation.
Upstream datasets and models remain governed by their respective terms. Public
availability is not a claim of conference-review anonymity.
