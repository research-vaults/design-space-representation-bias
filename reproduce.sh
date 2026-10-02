#!/usr/bin/env bash
set -euo pipefail

python3 src/verify_manifest.py
python3 src/replay_sampled_choices.py
python3 src/replay_confirmatory_choices.py
python3 src/replay_prompt_groups.py
python3 src/replay_knapsack_transport.py

echo "All release checks passed."
