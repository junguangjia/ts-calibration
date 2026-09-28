# Validation notes

## What actually ran

`pilot.py --reps 200` completed in a separate reference environment, producing 200 independent paths sharing innovations across comparison methods. Original coursework was not executed. Future-suffix/current-origin invariance, unit equivariance and oracle-radius identity checks passed.

`theory_checks.py` completed with 40,000 independent Monte Carlo calibration samples per configuration. It checks the finite-window contamination formula, the clean rank benchmark and stochastic-order direction. It uses a deterministic pattern of scale multipliers, not an estimated scale model.

## Numerical refinement

An initial 256/512 Gauss-Legendre comparison failed a 2e-8 tolerance for W=250, m=50, multiplier=3, with a difference about 3.03e-8. Increasing resolution to 512/1024 produced a difference about 4.02e-10; all four cases then satisfied 1e-8 agreement. Monte Carlo checks agreed within their recorded simulation errors. The final code preserves this higher-resolution check.

## Important interpretation checks

- W=50 and W=250 have different finite-rank reference coverage at nominal 95%; this is not all adaptivity.
- The oracle scale uses privileged information at an unannounced jump. It is a diagnostic control, not a deployable method.
- The headline pilot result (normalized EWMA W=250) is 95.241875% overall realized coverage and 83.42% over the first 25 post-upshift forecasts. Monte Carlo SEs across independent paths are about 0.0153 and 0.3546 percentage points, respectively. These are not universal performance estimates.
- In the exact contamination model, current scale is already correct, but 25 of 250 old scores inflated by factor 3 raise repeated-sample coverage to about 98.95534%, compared with the 95.21912% clean finite-rank benchmark. This numerical identity is not evidence of practical superiority or originality.
- No adaptive window candidate, SPCI, ACI, SAOCP, PID, fitted GARCH or real-data forecast benchmark was run.
- No complete new general coverage theorem or novelty review has been completed. Elementary proof sketches and a fixed-grid concentration route must be independently verified.
