"""Independent numerical checks of a finite-window scale-contamination identity.

The identity assumes independent continuous innovations and a DETERMINISTIC
pattern of calibration-score scale multipliers. It does not establish the same
binomial law for an EWMA/GARCH-estimated scale or outcome-selected windows.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.special import ndtr
from scipy.stats import binom, norm

ROOT = Path(__file__).resolve().parent


def new_result_directory(out: Path) -> None:
    """Keep numerical-check output out of reference snapshots and existing runs."""
    destination = out.resolve()
    results_root = (ROOT / 'results').resolve()
    if destination == results_root or not destination.is_relative_to(results_root):
        raise ValueError('Output must be a new directory below this project results/')
    destination.mkdir(parents=True, exist_ok=False)


def exact_coverage(window: int, contaminated: int, multiplier: float,
                   alpha: float = 0.05, nodes: int = 512) -> float:
    """Integrate over v=G(U0) ~ Uniform(0,1), where U=abs(N(0,1))."""
    if (not isinstance(window, int) or isinstance(window, bool) or window < 1
            or not isinstance(contaminated, int) or isinstance(contaminated, bool)
            or not 0 <= contaminated <= window
            or not math.isfinite(multiplier) or multiplier <= 0
            or not math.isfinite(alpha) or not 0 < alpha < 1
            or not isinstance(nodes, int) or isinstance(nodes, bool) or nodes < 2):
        raise ValueError('Invalid parameters')
    k = math.ceil((window + 1) * (1-alpha))
    if k > window:
        return 1.0
    x, weight = np.polynomial.legendre.leggauss(nodes)
    v = (x+1)/2
    u = norm.ppf((1+v)/2)
    p_contaminated = 2*ndtr(u/multiplier)-1
    b = np.arange(contaminated+1)
    probabilities = binom.pmf(b[None, :], contaminated, p_contaminated[:, None])
    probabilities *= binom.cdf(k-1-b[None, :], window-contaminated, v[:, None])
    return float(np.dot(weight/2, probabilities.sum(axis=1)))


def monte_carlo(window: int, contaminated: int, multiplier: float,
                reps: int = 40000) -> tuple[float, float]:
    if (not isinstance(window, int) or isinstance(window, bool) or window < 1
            or not isinstance(contaminated, int) or isinstance(contaminated, bool)
            or not 0 <= contaminated <= window
            or not math.isfinite(multiplier) or multiplier <= 0
            or not isinstance(reps, int) or isinstance(reps, bool) or reps < 2):
        raise ValueError('Invalid Monte Carlo parameters')
    rng = np.random.default_rng(902026 + contaminated)
    k = math.ceil((window+1)*0.95)
    estimates = []
    for start in range(0, reps, 1000):
        scores = np.abs(rng.normal(size=(min(1000, reps-start), window)))
        scores[:, :contaminated] *= multiplier
        q = np.partition(scores, k-1, axis=1)[:, k-1]
        estimates.append(2*ndtr(q)-1)
    values = np.concatenate(estimates)
    return float(values.mean()), float(values.std(ddof=1)/np.sqrt(reps))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True,
                        help='New directory below this project results/.')
    out = parser.parse_args().out
    new_result_directory(out)
    rows = []
    for m, c in [(0, 1.0), (25, 3.0), (25, 1/3), (50, 3.0)]:
        q512 = exact_coverage(250, m, c, nodes=512)
        q1024 = exact_coverage(250, m, c, nodes=1024)
        empirical, mcse = monte_carlo(250, m, c)
        assert abs(q512-q1024) < 1e-8
        assert abs(q1024-empirical) < 6*mcse
        base = math.ceil(251*0.95)/251
        if c > 1:
            assert q1024 > base
        elif c < 1:
            assert q1024 < base
        else:
            assert abs(q1024-base) < 1e-10
        rows.append({'window': 250, 'm': m, 'multiplier': c,
                     'quadrature_512': q512, 'quadrature_1024': q1024,
                     'mc_reps': 40000, 'mc_conditional_coverage_mean': empirical,
                     'mcse': mcse, 'iid_rank_coverage': base})
    with (out/'coverage_identity.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    (out/'checks.json').write_text(json.dumps({
        'checks': 'quadrature agreement, independent MC, rank baseline, monotonicity passed',
        'mc_seed_rule': '902026 + contaminated',
        'mc_reps_per_configuration': 40000,
        'not_proven_by_tests': 'Mathematical validity in general or originality',
        'assumptions': 'Known zero mean; independent Gaussian innovations; deterministic multiplier pattern'
    }, indent=2))
    for row in rows:
        print(row)

if __name__ == '__main__':
    main()
