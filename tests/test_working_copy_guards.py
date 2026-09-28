"""Input and output guards for the supplied scripts' editable working copies."""

from pathlib import Path

import numpy as np
import pytest

from pilot import causal_ewma, new_result_directory as pilot_output, rolling_radius
from theory_checks import exact_coverage, new_result_directory as theory_output


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('decay, initial_variance', [
    (0.0, 1.0), (1.0, 1.0), (float('nan'), 1.0), (0.5, float('inf')),
])
def test_ewma_rejects_invalid_parameters(decay, initial_variance):
    with pytest.raises(ValueError):
        causal_ewma(np.ones((1, 4)), decay, initial_variance)


def test_ewma_rejects_nonfinite_outcomes():
    with pytest.raises(ValueError):
        causal_ewma(np.array([[1.0, float('nan')]]), 0.5, 1.0)


@pytest.mark.parametrize('window, alpha, start', [
    (0, 0.05, 4), (4, 0.0, 4), (4, 1.0, 4), (4, 0.05, 3), (4, 0.05, 5),
])
def test_rolling_radius_rejects_invalid_protocol_parameters(window, alpha, start):
    with pytest.raises(ValueError):
        rolling_radius(np.ones((1, 5)), np.ones((1, 5)), window, alpha, start)


def test_rolling_radius_rejects_nonfinite_scale_and_outcome():
    with pytest.raises(ValueError):
        rolling_radius(np.ones((1, 5)), np.array([[1, 1, 1, np.inf, 1]]), 3, 0.05, 3)
    with pytest.raises(ValueError):
        rolling_radius(np.array([[1, 1, np.nan, 1, 1]]), np.ones((1, 5)), 3, 0.05, 3)


@pytest.mark.parametrize('window, contaminated, multiplier, alpha, nodes', [
    (0, 0, 1.0, 0.05, 16), (5, 6, 1.0, 0.05, 16),
    (5, 1, 0.0, 0.05, 16), (5, 1, 1.0, 1.0, 16), (5, 1, 1.0, 0.05, 1),
])
def test_exact_coverage_rejects_invalid_inputs(window, contaminated, multiplier, alpha, nodes):
    with pytest.raises(ValueError):
        exact_coverage(window, contaminated, multiplier, alpha=alpha, nodes=nodes)


@pytest.mark.parametrize('guard', [pilot_output, theory_output])
def test_working_copy_output_must_be_fresh_under_results(guard):
    with pytest.raises(ValueError):
        guard(ROOT / 'reference' / 'uncreated-output')
    with pytest.raises(ValueError):
        guard(ROOT / 'results')
