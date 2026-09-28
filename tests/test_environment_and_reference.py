"""Lightweight acceptance tests, not proofs or a full scientific reproduction."""
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
import pytest
from scipy.special import ndtr
from scipy.stats import norm
from pilot import causal_ewma, rolling_radius
from theory_checks import exact_coverage

ROOT = Path(__file__).resolve().parents[1]

def test_isolated_interpreter():
    assert sys.prefix != sys.base_prefix
    assert Path(sys.prefix).resolve() == (ROOT/'.venv').resolve()

def test_synthetic_baseline_integrity():
    packet = ROOT/'reference/synthetic_baseline_v1'
    entries = (packet/'SHA256SUMS.txt').read_text().splitlines()
    assert len(entries) == 6
    for line in entries:
        digest, rel = line.split(maxsplit=1)
        assert hashlib.sha256((packet/rel).read_bytes()).hexdigest() == digest, rel

def test_private_reference_integrity():
    path = ROOT/'reference/manifest.json'
    if not path.exists():
        pytest.skip('Private local reference manifest is not distributed with Git')
    manifest = json.loads(path.read_text())
    for item in manifest['coursework']:
        assert hashlib.sha256((ROOT/item['snapshot']).read_bytes()).hexdigest() == item['sha256']
        original = Path(item['original'])
        if original.is_file():
            assert hashlib.sha256(original.read_bytes()).hexdigest() == item['sha256']

def test_ewma_predict_before_update():
    y = np.array([[2.0, 0.0, 3.0]])
    scales = causal_ewma(y, 0.5, 1.0)
    np.testing.assert_allclose(scales**2, [[1.0, 2.5, 1.25]])

def test_current_and_future_outcomes_do_not_change_issued_intervals():
    y = np.random.default_rng(18).normal(size=(2, 150))
    mutated = y.copy()
    mutated[:, 80:] += 1000
    s1 = causal_ewma(y, 0.94, 1.0)
    s2 = causal_ewma(mutated, 0.94, 1.0)
    np.testing.assert_array_equal(s1[:, :81], s2[:, :81])
    r1 = rolling_radius(y, s1, 39, 0.05, 40)
    r2 = rolling_radius(mutated, s2, 39, 0.05, 40)
    np.testing.assert_array_equal(r1[:, 40:81], r2[:, 40:81])

@pytest.mark.parametrize('factor', [0.3, 7.0])
def test_unit_equivariance(factor):
    y = np.random.default_rng(19).normal(size=(2, 150))
    scale = causal_ewma(y, 0.94, 1.0)
    radius = rolling_radius(y, scale, 39, 0.05, 40)
    scaled = causal_ewma(factor*y, 0.94, factor**2)
    transformed = rolling_radius(factor*y, scaled, 39, 0.05, 40)
    np.testing.assert_allclose(transformed[:, 40:], factor*radius[:, 40:], rtol=1e-12)

@pytest.mark.parametrize('factor', [0.3, 7.0])
def test_common_scale_bias_cancels(factor):
    z = np.random.default_rng(20).normal(size=(2, 150))
    sigma = np.broadcast_to(np.linspace(1.0, 3.0, 150), z.shape)
    y = z*sigma
    oracle = rolling_radius(y, sigma, 39, 0.05, 40)
    biased = rolling_radius(y, factor*sigma, 39, 0.05, 40)
    np.testing.assert_allclose(biased[:, 40:], oracle[:, 40:], rtol=1e-12)

def test_tied_scores():
    y = np.ones((1, 50))
    radius = rolling_radius(y, y.copy(), 39, 0.05, 39)
    np.testing.assert_array_equal(radius[:, 39:], np.ones((1, 11)))

def test_unavailable_rank_is_infinite():
    y = np.ones((1, 20))
    radius = rolling_radius(y, y.copy(), 9, 0.05, 9)
    assert np.isinf(radius[:, 9:]).all()

def test_bad_scale_rejected():
    with pytest.raises(ValueError):
        rolling_radius(np.ones((1,50)), np.zeros((1,50)), 39, 0.05, 39)

def test_clean_small_window_rank_identity():
    p = exact_coverage(39, 0, 1.0, nodes=96)
    expected = math.ceil(40*0.95)/40
    assert abs(p-expected) < 1e-10

@pytest.mark.parametrize('multiplier', [0.5, 1.0, 2.0])
def test_deterministic_contamination_direction(multiplier):
    p = exact_coverage(39, 5, multiplier, nodes=96)
    if multiplier < 1:
        assert p < 0.95
    elif multiplier > 1:
        assert p > 0.95
    else:
        assert abs(p-0.95) < 1e-10

def test_gaussian_oracle_probability():
    critical = norm.ppf(0.975)
    assert abs((2*ndtr(critical)-1)-0.95) < 1e-14
