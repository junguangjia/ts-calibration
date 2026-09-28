# Sequential research protocol

Status: architecture contract for this research-feasibility workspace. It does
not assert a coverage theorem, numerical reproduction, or a new method.

## Language and scope

Python is the canonical implementation for sequential intervals, data-generating
processes, forecasting, calibration, metrics, evaluation, tests, and experiment
records. The root `pilot.py` and `theory_checks.py` are working copies of the
supplied development references. New research algorithms belong in `src/tscal/`.

`reference/r/` is an optional, independent check of classical ARMA/ARIMA,
GARCH(1,1), and residual diagnostics. It does not mirror the Python calibration
methods and is not required by the basic Python tests. The public synthetic
baseline is in `reference/synthetic_baseline_v1/`; original coursework is not
distributed. Julia is not part of this architecture.

The minimal implemented Python API is `src/tscal/protocol.py`:
`Forecast(mu_hat, sigma_hat, fit_cutoff)`,
`RollingConfig(method, window, alpha, evaluation_start)`,
`run_rolling_prequential(outcomes, forecaster, config)`, and
`common_evaluation_origins(*results)`. The callback receives an immutable tuple
of past outcomes and returns a forecast. The result keeps separate immutable
issued-interval and revealed-outcome records, including statuses for fits and
scores that could not be used. This API implements only symmetric fixed-window
calibration; it is not ACI, SPCI, or a general forecasting framework. A callback
can still capture external variables through a Python closure, so reviewers
must check that an experiment does not smuggle simulation truth through it.

## One forecast origin

At zero-based origin `t`, the information available to a deployable method is
the observations through `t-1`, previously issued forecasts and intervals,
previously revealed errors, and tuning choices fixed by the declared protocol.
The method must complete these steps in order:

1. Fit or update the location and scale predictors with a cutoff strictly before
   `t`; record that cutoff, `mu_hat[t]`, and positive `sigma_hat[t]`.
2. Select eligible *historical vintage* scores and a calibration rule using only
   that information. A vintage score at `i` is
   `abs(Y[i] - mu_hat[i]) / sigma_hat[i]`, using the estimates saved at origin
   `i`, before `Y[i]` was observed.
3. Construct and save the interval, calibration count/rank, method identity,
   window or weights, and controller state before revealing `Y[t]`.
4. Reveal `Y[t]`; compute coverage/error and the new score from the saved
   forecast-origin estimates. Append this score without changing older scores.
5. Update filtering and calibration/controller state for origin `t+1`.

For a fixed window of `W` scores and target `1-alpha`, the corrected order is
`k = ceil((W+1)*(1-alpha))`. If `k > W`, the specified finite-sample threshold is
infinite. A method that clips this threshold, substitutes the sample maximum,
or removes an extreme score is a distinct variant and needs its own name and
evaluation. Ties and unavailable calibration history need explicit conventions.

Do not fit, center, standardize, choose models, or choose tuning parameters from
the full evaluation series before sequential forecasting. Retrospectively
recomputing old scores with a later fitted model changes the method. Online
updates may use an outcome after it has been revealed, but only for later
origins. Record failed fits and unavailable forecasts; compare methods on the
same predeclared eligible origins rather than silently dropping difficult dates.
`planned_evaluation_origins` and `issued_evaluation_origins` distinguish the
predeclared dates from dates with issued intervals. The helper
`common_evaluation_origins` retains common planned dates even when a method
failed. Report each method's issued/failure counts and the fate of every
planned date; do not summarize only successful dates as if they were the full
evaluation.

Simulation truth, including true conditional scales, change points, and oracle
innovation parameters, is reserved for named oracle diagnostics and evaluation.
Deployable method inputs must not contain it.

## Evidence and run records

The supplied pilot, its seeds, any matching reproductions, and current
architecture checks are **development** evidence. Confirmation requires a
separate locked protocol with new seeds and predeclared scenarios, tuning,
origins, endpoints, and primary contrasts. Do not promote development outputs
to confirmation by changing a label.

Each experiment run should retain an immutable configuration snapshot; unique
run ID; development or confirmation status; seed sequence or other randomness
record; dependency and environment versions; source revision when a commit
exists, otherwise source hashes; resource limits; method names and information
sets; identical planned evaluation origins; and all failures. Store intervals
and vintage-score/cutoff traces for selected paths and event windows, plus
per-replication metrics for every attempted configuration. Use paired independent
paths as the unit for Monte Carlo uncertainty, not adjacent forecast dates.

The existing `make test`, `make smoke`, and `make reproduce` commands use a
bounded one-worker runner and fresh `results/<run_id>/` folders. Tests cover
the new protocol and the archived development baseline; smoke and reproduce
run the exploratory simulation. Running a direct root script requires an
explicit new output path beneath this workspace's `results/`. The architecture
runs were made before an initial Git commit, so their manifests record source
hashes and no revision. A later commit does not retroactively change those run
identities.

## Method fidelity and interpretation

Read each original paper and author implementation before adding ACI, SPCI,
SAOCP, or Conformal PID. Record paper version, relevant theorem/section,
repository URL, commit, license, deviations, score convention, and required
quantile or feedback behavior. Distinguish a shared-predictor calibration
comparison from a faithful end-to-end reproduction. Do not transfer a theorem
to an altered local variant.

Classical full-sample coursework fits can check numerical calculations, but
they cannot be used as out-of-sample forecasts. Any sequential ARMA/GARCH
benchmark must fit on outcomes strictly before each origin. The HW5
`alpha + beta = 1` case is a labeled boundary/stress case, not a standard
covariance-stationary GARCH reference. The legacy IBM series has no verified
dates or source license for research redistribution.
