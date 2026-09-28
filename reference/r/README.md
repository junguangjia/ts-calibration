# Classical R reference

Python in `src/tscal/` is the canonical research implementation. This small R
layer supplies independent classical time-series calculations. It does not
implement conformal or online calibration methods and is not required by the
Python tests.

## Scope and provenance

- `arma_reference.R`: predeclared ARMA/ARIMA order fitted with `stats::arima`
  by maximum likelihood, followed by a one-step mean and standard-error
  forecast. There is no automatic order search over an evaluation segment.
  A mean term is allowed only for an undifferenced ARMA fit; optimizer
  nonconvergence is an error.
- `garch_reference.R`: a local, transparent Gaussian quasi-maximum-likelihood
  fit of a **zero-mean** GARCH(1,1), with variance recursion
  `h[i] = omega + alpha*x[i-1]^2 + beta*h[i-1]`. The optimizer constrains
  `omega > 0`, `alpha > 0`, `beta > 0`, and `alpha + beta < 1`. It reports
  convergence and whether a search bound was reached. This is an independent
  numerical reference, **not** an authoritative `fGarch` or `rugarch` fit.
- `diagnostics.R`: descriptive Ljung-Box tests on residuals and squared
  residuals, plus a lagged-squares ARCH LM statistic. Their approximate
  p-values do not prove model adequacy, especially after model selection.
- `validation.R`: deterministic synthetic smoke check and a machine-readable
  CSV summary. It writes R session and source-hash records.

Both fitting functions use one-based `origin`: the forecasted outcome is
`y[origin]`, and `fit_cutoff = origin - 1`. They fit **only** the prefix through
that cutoff, including when a longer vector is supplied. The current and
future outcomes can be unavailable. For GARCH, `innovations` must already be
zero-mean errors or causally produced forecast errors; this function does not
perform full-sample centering. Every refit is on the available prefix, so a
sequential benchmark must call it at each scheduled origin and save the
forecast before revealing the outcome. A production benchmark should also
record its fitting schedule and failures.

The returned fitted residuals are retrospective diagnostics from a model fit
on the whole *available prefix*. They are **not** forecast-origin vintage
scores and must never be inserted into an online calibration history. Vintage
scores require predictions recorded at each historical origin before its
outcome was revealed. Full-series IBM/STAT 5221 computations in the private
coursework are useful only as legacy in-sample checks; the IBM date provenance
is unresolved. This R layer does not read, modify, or reproduce those private
files by default.

The legacy HW5 simulation has `alpha = beta = 0.5`, hence
`alpha + beta = 1`. That is a finite unconditional second-moment boundary and
belongs to a separately labeled stress analysis. The stationary-interior
GARCH fitter here deliberately excludes it; no ordinary covariance-stationary
interpretation or automatic conversion of that homework fit is claimed.

## Run the smoke check

From the project root, give a **new** direct child of `results/`:

```sh
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 \
  Rscript reference/r/validation.R results/r-smoke-local-001
```

Choose an unused directory name for each run; the script refuses an existing
output path. `validation.csv` contains one
metric per row, including fit cutoffs, one-step forecasts, optimization flags,
diagnostics, and the current/future mutation-invariance check.
`config.csv` fixes the development-smoke seed, DGPs, burn-in and fit choices;
`fit_status.csv` records the optimizer's convergence message;
`source_md5.csv` hashes these R files; `session.txt` records the seed, model
choices, R platform, and explicit base package/session versions. These are reference smoke
results, not a GARCH estimator benchmark or a cross-language numerical
equivalence claim. The checked local run is
`results/20260928T021833Z-r-reference-5221/`: R 4.5.3, base `stats` and
`utils`; no external GARCH package or global package installation was used.

For a later Python comparison, supply the same frozen numeric prefix and
predeclared model/order to each language, record the forecast origin and fit
cutoff, and compare the resulting CSV forecasts with a tolerance chosen for
the two different optimizer/filter conventions. A matching answer would test
implementation agreement, not establish a general coverage guarantee.
