# Exploratory synthetic baseline, version 1

These files are the archived outputs of the 200-replication synthetic pilot and
the finite-window numerical checks described in `research_design.md` and
`validation_notes.md`. They are development evidence from a single controlled
scenario, not independent confirmation or a claim of methodological novelty.

The pilot configuration, random seed, and software versions are recorded in
`pilot_results/environment.json`. `pilot_results/replicates.csv` provides the
per-replication metrics used by `scripts/compare_reference.py`.
`pilot_results/summary.csv` and `trajectory.csv` retain the aggregate and
event-time summaries. The theory outputs are in `theory_results/`.

`SHA256SUMS.txt` records the hashes of the six numerical files. A fresh local
run writes to a new `results/<run_id>/` folder; these archived files should not
be overwritten.
