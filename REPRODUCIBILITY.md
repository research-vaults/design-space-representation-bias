# Reproducibility contract

## Scientific unit

A written menu is a presentation of candidate policies. An executable behavioural class groups entries that produce identical campaign behaviour on frozen probe states. All choice comparisons in this release are made after aggregating written-entry probabilities over those executable classes.

## Replay boundaries

### Sampled choices

`src/replay_sampled_choices.py` reads the frozen per-call choices directly, validates their schema and mapping to the menu-specific executable class, checks matched scheduled-call counts, and independently recomputes the reported excess total-variation distance. The frozen schedule contains 8,088 call records; 31 unavailable responses are represented explicitly as null selections and excluded from empirical choice distributions.

### Confirmatory choices

`src/replay_confirmatory_choices.py` reconstructs 1,176 model/landscape/arm cells from the frozen distributions and independently recomputes replicate floors, no-op mass, canonical-minus-rewritten discovery AUC, and representation-ensemble contrasts.

### Prompt groups

`src/replay_prompt_groups.py` treats distinct prompt strings—not landscapes receiving byte-identical strings—as the choice-side replication unit. It reproduces prompt-group sensitivity and two empirical floors: same-batch canonical replication and cross-time, byte-identical prompts.

### Knapsack transport

`src/replay_knapsack_transport.py` executes all eight policies over the frozen probe and audit instances, verifies distinct executable classes, checks every written-space and permutation mapping, audits probability aggregation from written entries to executable classes, and independently recomputes the transport criteria.

## Data provenance

The protein-choice JSON files contain cached model selections or distributions and execution-derived summaries. The public protein fitness tables used to construct utilities are not redistributed. They can be obtained from the SSMuLA release (Zenodo DOI `10.5281/zenodo.13910506`) subject to its own terms.

The knapsack benchmark is synthetic and fully bundled. Its frozen instances are sufficient for all included transport checks.

## Determinism

The numerical replays are deterministic except for bootstrap resampling in the prompt-group audit, which uses a fixed seed. Small floating-point differences across NumPy/platform versions are tolerated only at the explicit thresholds in each script.

## Integrity

`MANIFEST.sha256` pins every tracked release file except the manifest itself. Run `python src/verify_manifest.py` before interpreting results. A checksum mismatch indicates that the release no longer matches the audited snapshot.
