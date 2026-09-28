"""Mechanism pilot: causal scale forecasts and vintage-score calibration.

This is a synthetic, exploratory experiment, not a reproduction of the user's
coursework and not an implementation of SPCI/ACI. It tests no novelty claim.
Run: python pilot.py --out results --reps 200
Dependencies: numpy, scipy (recorded in environment.json).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.special import ndtr
from scipy.stats import norm

ALPHA = 0.05
SEED = 20260928
N = 2600
EVAL_START = 1000
UP = 1200
DOWN = 1800
EWMA_LAMBDA = 0.94
PERIODS = {
    'all_test': (EVAL_START, N),
    'pre_shift': (1000, 1200),
    'up_0_24': (1200, 1225),
    'up_50_249': (1250, 1450),
    'high_late': (1600, 1800),
    'down_0_24': (1800, 1825),
    'down_50_249': (1850, 2050),
    'final_low': (2350, 2600),
}
ROOT = Path(__file__).resolve().parent


def new_result_directory(out: Path) -> None:
    """Keep working-copy outputs fresh and separate from source snapshots."""
    destination = out.resolve()
    results_root = (ROOT / 'results').resolve()
    if destination == results_root or not destination.is_relative_to(results_root):
        raise ValueError('Output must be a new directory below this project results/')
    destination.mkdir(parents=True, exist_ok=False)


def causal_ewma(y: np.ndarray, decay: float, initial_variance: float) -> np.ndarray:
    """Scale at t uses y[:t] only. Mean is KNOWN to be zero in this pilot."""
    if (y.ndim != 2 or not all(y.shape) or not np.isfinite(y).all()
            or not math.isfinite(decay) or not 0 < decay < 1
            or not math.isfinite(initial_variance) or initial_variance <= 0):
        raise ValueError('Invalid EWMA input')
    result = np.empty_like(y, dtype=float)
    state = np.full(y.shape[0], initial_variance, dtype=float)
    for t in range(y.shape[1]):
        result[:, t] = np.sqrt(state)
        state = decay * state + (1.0 - decay) * y[:, t] ** 2
    return result


def rolling_radius(y: np.ndarray, scale: np.ndarray, window: int,
                   alpha: float, start: int) -> np.ndarray:
    """Use scores y_i / scale_i saved at their ORIGINAL forecast origins.

    k=ceil((W+1)*(1-alpha)); an unavailable kth rank yields infinite radius.
    This rank correction alone does NOT guarantee coverage under dependence.
    The current outcome y_t is excluded from the t-th calibration window.
    """
    if (y.ndim != 2 or scale.ndim != 2 or y.shape != scale.shape
            or not all(y.shape) or not np.isfinite(y).all()
            or not np.isfinite(scale).all() or np.any(scale <= 0)
            or not isinstance(window, int) or isinstance(window, bool)
            or not 1 <= window < y.shape[1]
            or not isinstance(start, int) or isinstance(start, bool)
            or not window <= start < y.shape[1]
            or not math.isfinite(alpha) or not 0 < alpha < 1):
        raise ValueError('Invalid calibration input')
    k = math.ceil((window + 1) * (1.0 - alpha))
    scores = np.abs(y) / scale
    result = np.full(y.shape, np.nan)
    if k > window:
        result[:, start:] = np.inf
        return result
    for t in range(start, y.shape[1]):
        historical = scores[:, t-window:t]
        quantile = np.partition(historical, k-1, axis=1)[:, k-1]
        result[:, t] = scale[:, t] * quantile
    return result


def run(out: Path, reps: int) -> None:
    if reps < 2:
        raise ValueError('At least two independent replicates required')
    new_result_directory(out)
    seeds = np.random.SeedSequence(SEED).spawn(reps)
    z = np.stack([np.random.default_rng(s).normal(size=N) for s in seeds])
    true_scale_1d = np.ones(N)
    true_scale_1d[UP:DOWN] = 3.0
    true_scale = np.broadcast_to(true_scale_1d, z.shape)
    y = true_scale * z
    ewma = causal_ewma(y, EWMA_LAMBDA, initial_variance=1.0)
    ones = np.ones_like(y)
    critical = float(norm.ppf(1 - ALPHA/2))
    radii = {
        'raw_W250': rolling_radius(y, ones, 250, ALPHA, EVAL_START),
        'raw_W50': rolling_radius(y, ones, 50, ALPHA, EVAL_START),
        'ewma_W250': rolling_radius(y, ewma, 250, ALPHA, EVAL_START),
        'ewma_W50': rolling_radius(y, ewma, 50, ALPHA, EVAL_START),
        'ewma_Gaussian': ewma * critical,
        'oracle_scale_W250': rolling_radius(y, true_scale, 250, ALPHA, EVAL_START),
        'oracle_full': true_scale * critical,
    }
    # Causality: modifying all outcomes at/after cut must NOT affect a forecast
    # made at cut, nor any preceding forecast.
    test_y = y[:2, :1300].copy()
    cut = 1100
    mutated = test_y.copy()
    mutated[:, cut:] += 1000.0
    a = causal_ewma(test_y, EWMA_LAMBDA, 1.0)
    b = causal_ewma(mutated, EWMA_LAMBDA, 1.0)
    np.testing.assert_array_equal(a[:, :cut+1], b[:, :cut+1])
    ra = rolling_radius(test_y, a, 250, ALPHA, EVAL_START)
    rb = rolling_radius(mutated, b, 250, ALPHA, EVAL_START)
    np.testing.assert_array_equal(ra[:, EVAL_START:cut+1], rb[:, EVAL_START:cut+1])
    factor = 7.0
    a_scaled = causal_ewma(test_y * factor, EWMA_LAMBDA, factor**2)
    r_scaled = rolling_radius(test_y * factor, a_scaled, 250, ALPHA, EVAL_START)
    np.testing.assert_allclose(r_scaled[:, EVAL_START:], ra[:, EVAL_START:] * factor,
                               rtol=2e-13, atol=1e-12)
    np.testing.assert_allclose(radii['oracle_full'] / true_scale, critical)

    summary, replicate_rows, trajectory_rows = [], [], []
    for method, radius in radii.items():
        cond_cov = 2 * ndtr(radius / true_scale) - 1
        coverage = (np.abs(y) <= radius).astype(float)
        normalized_width = radius / (true_scale * critical)
        interval_score = 2*radius + (2/ALPHA)*np.maximum(np.abs(y)-radius, 0)
        metrics = {
            'coverage': coverage,
            'conditional_coverage': cond_cov,
            'width_ratio_to_oracle': normalized_width,
            'interval_score': interval_score,
            'scale_normalized_interval_score': interval_score / true_scale,
        }
        for period, (lo, hi) in PERIODS.items():
            row = {'method': method, 'period': period, 'reps': reps, 'times': hi-lo}
            for metric, values in metrics.items():
                per_rep = values[:, lo:hi].mean(axis=1)
                row[metric] = float(per_rep.mean())
                row[metric + '_mcse'] = float(per_rep.std(ddof=1)/math.sqrt(reps))
                for rep, value in enumerate(per_rep):
                    replicate_rows.append({'method': method, 'period': period,
                                           'replicate': rep, 'metric': metric,
                                           'value': float(value)})
            summary.append(row)
        for t in range(EVAL_START, N):
            trajectory_rows.append({
                'method': method, 't': t, 'true_scale': true_scale_1d[t],
                'conditional_coverage_mean': float(cond_cov[:, t].mean()),
                'coverage_mean': float(coverage[:, t].mean()),
                'width_ratio_mean': float(normalized_width[:, t].mean()),
            })
    for filename, rows in [('summary.csv', summary), ('replicates.csv', replicate_rows),
                           ('trajectory.csv', trajectory_rows)]:
        with (out / filename).open('w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    meta = {
        'purpose': 'Exploratory synthetic mechanism pilot; no novelty/performance claim',
        'seed': SEED, 'reps': reps, 'N': N, 'evaluation_start': EVAL_START,
        'scale_jumps_zero_based': {str(UP): 3.0, str(DOWN): 1.0},
        'alpha': ALPHA, 'ewma_decay': EWMA_LAMBDA,
        'location': 'Known zero, fixed for every method',
        'noise': 'Independent standard Gaussian',
        'score_storage': 'Immutable vintage / forecast-origin scales',
        'oracle_visibility': 'True scales used only in explicitly named oracle methods and diagnostics',
        'tests': ['future-suffix invariance passed', 'scale equivariance passed',
                  'oracle radius identity passed'],
        'limitations': ['One controlled scale scenario, one EWMA setting',
                        'Not GARCH; not original homework execution',
                        'No ACI/SPCI/SAOCP/PID comparison',
                        'No new candidate method tested; no confirmatory test set'],
        'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__,
    }
    (out / 'environment.json').write_text(json.dumps(meta, indent=2))
    print('Completed mechanism pilot. Results:', out)
    for row in summary:
        if row['period'] in ['all_test', 'up_0_24', 'up_50_249', 'down_50_249']:
            print(row['method'], row['period'], 'coverage=', round(row['coverage'], 4),
                  'conditional=', round(row['conditional_coverage'], 4),
                  'width/oracle=', round(row['width_ratio_to_oracle'], 3))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True,
                        help='New directory below this project results/')
    parser.add_argument('--reps', type=int, default=200)
    args = parser.parse_args()
    run(args.out, args.reps)
