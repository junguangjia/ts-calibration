# TS Calibration

Research-feasibility code for volatility-estimation lag and calibration memory
in sequential prediction intervals. No new method or research contribution has
been verified.

Python is the canonical research implementation. R provides an optional,
independent reference for classical time-series fitting and diagnostics; it is
not a second implementation of the conformal methods. Julia is not used.

## Start

Read `docs/protocol.md` before new experiments. `research_design.md` describes
the proposed mechanism, assumptions, and open scientific questions; it is not
a verified result. `validation_notes.md` records the scope of the numerical
checks.

The [feasibility report](latex/ts-calibration-report.pdf) summarizes the
finite-window mechanism and archived synthetic pilot. Its editable
[LaTeX source](latex/ts-calibration-report.tex) is included. The report is
development evidence, not a new-method or general-coverage claim. Compile the
standalone source twice with `pdflatex` to resolve cross-references.

## Run
Use Python 3.12.9 and [uv](https://docs.astral.sh/uv/) on `PATH`. From the
repository root:

```sh
make setup      # create/sync the local .venv from uv.lock
make test       # Python tests; R is optional
make smoke      # two-path development reference check
```

`make setup` requires a locally available Python 3.12.9 and does not download
another interpreter. `make reproduce` runs the 200-path exploratory pilot and
theory checks into a new directory. A full reproduction has not yet been
recorded for this repository state.
Each test, smoke, or reproduction run creates a fresh `results/<run_id>/`
folder with logs and a run record. Direct calls to `pilot.py` or
`theory_checks.py` require an explicit,
new `--out` path beneath this workspace's `results/`. Keep one CPU worker and
one BLAS thread by default.
For a direct script importing the canonical `tscal` module, run from the root
with `PYTHONPATH=src .venv/bin/python your_script.py`; pytest already includes
`src` on its import path.

## Layout
- `pilot.py`, `theory_checks.py`: exploratory simulation and numerical checks.
- `src/tscal/`: canonical Python research protocol and future methods.
- `latex/`: standalone feasibility report and compiled PDF.
- `reference/r/`: optional independent classical statistical reference.
- `reference/synthetic_baseline_v1/`: archived exploratory synthetic outputs
  with SHA-256 checksums.
- `scripts/run.py`: bounded runner; new logs/results for every invocation.
- `tests/`: research invariants and environment/reference checks.
- `docs/protocol.md`: forecast-before-reveal contract and run evidence.
- `results/<run_id>/`: local outputs, ignored by Git.

The synthetic baseline supports `scripts/compare_reference.py`, which compares
matching per-replication metrics from a fresh run. Original coursework and the
IBM data are excluded from this repository.

Current pilot seeds and matching reproductions are development evidence, not
locked confirmation. The two-path smoke comparison passed; no full pilot
reproduction, scientific proof, or novelty verification is claimed. Do not
execute the original scripts into reference result directories.

## License

The code, documentation, and synthetic reference data in this
repository are available under the [MIT License](LICENSE). Referenced papers
remain with their respective publishers and authors. Original Columbia
coursework, instructor materials, and the IBM dataset are not included.
