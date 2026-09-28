"""Research invariants for the canonical forecast-before-reveal protocol."""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from tscal.protocol import (
    Forecast,
    ProtocolViolation,
    RollingConfig,
    common_evaluation_origins,
    run_rolling_prequential,
)


def config(window=3, alpha=0.5, evaluation_start=3, method="rolling"):
    return RollingConfig(method, window, alpha, evaluation_start)


def fixed_forecast(history):
    return Forecast(0.0, 1.0, len(history) - 1)


def test_forecaster_sees_only_immutable_observed_prefix_and_input_is_unchanged():
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    original = y.copy()
    seen = []

    def forecaster(history):
        assert isinstance(history, tuple)
        seen.append(history)
        return fixed_forecast(history)

    result = run_rolling_prequential(y, forecaster, config())
    assert seen == [(), (1.0,), (1.0, 2.0), (1.0, 2.0, 3.0),
                    (1.0, 2.0, 3.0, 4.0)]
    np.testing.assert_array_equal(y, original)
    assert [row.origin for row in result.issues] == list(range(len(y)))
    assert [row.origin for row in result.revealed] == list(range(len(y)))


def test_each_outcome_is_read_only_after_its_forecast():
    events = []
    values = [1.0, 2.0, 3.0, 4.0]

    class LoggedSequence:
        def __len__(self):
            return len(values)

        def __getitem__(self, origin):
            events.append(("reveal", origin))
            return values[origin]

    def forecaster(history):
        events.append(("forecast", len(history)))
        return fixed_forecast(history)

    run_rolling_prequential(LoggedSequence(), forecaster, config())
    assert events == [event for origin in range(4)
                      for event in (("forecast", origin), ("reveal", origin))]


def test_same_origin_and_future_outcome_mutation_cannot_change_issued_interval():
    original = run_rolling_prequential([1, 2, 3, 4, 5], fixed_forecast, config())
    mutated = run_rolling_prequential([1, 2, 3, 400, 500], fixed_forecast, config())
    assert original.issues[:4] == mutated.issues[:4]
    assert original.revealed[3].vintage_score == 4
    assert mutated.revealed[3].vintage_score == 400


def test_vintage_scores_use_original_forecast_and_are_immutable():
    def changing_scale(history):
        return Forecast(0.0, 2.0 ** len(history), len(history) - 1)

    result = run_rolling_prequential([4, 4, 4, 4], changing_scale, config())
    assert [row.vintage_score for row in result.revealed] == [4.0, 2.0, 1.0, 0.5]
    assert (result.issues[3].lower, result.issues[3].upper) == (-16.0, 16.0)
    with pytest.raises(FrozenInstanceError):
        result.revealed[0].vintage_score = 999


def test_invalid_or_future_fit_cutoffs_are_rejected():
    with pytest.raises(ProtocolViolation, match="fit_cutoff"):
        run_rolling_prequential([1, 2, 3, 4],
                                lambda history: Forecast(0, 1, len(history)), config())
    with pytest.raises(ProtocolViolation, match="fit_cutoff"):
        run_rolling_prequential([1, 2, 3, 4],
                                lambda history: Forecast(0, 1, -2), config())


def test_fit_failure_keeps_date_and_does_not_backfill_older_scores():
    def sometimes_fails(history):
        if len(history) == 2:
            raise RuntimeError("private diagnostic text is not copied")
        return fixed_forecast(history)

    result = run_rolling_prequential([1] * 7, sometimes_fails, config())
    assert result.issues[2].status == "fit_failed"
    assert result.issues[2].failure_type == "RuntimeError"
    assert result.revealed[2].status == "unscored_forecast"
    assert result.issues[3].status == "insufficient_calibration"
    assert result.issues[3].calibration_count == 2
    assert result.issues[5].status == "insufficient_calibration"
    assert result.issues[6].status == "issued"
    assert result.planned_evaluation_origins == (3, 4, 5, 6)
    assert result.issued_evaluation_origins == (6,)


def test_rank_ties_and_unavailable_rank():
    tied = run_rolling_prequential([2] * 5, fixed_forecast, config())
    assert tied.issues[3].rank == 2
    assert (tied.issues[3].lower, tied.issues[3].upper) == (-2, 2)

    infinite = run_rolling_prequential([1] * 5, fixed_forecast,
                                       config(window=3, alpha=0.05))
    assert infinite.issues[3].rank == 4
    assert (infinite.issues[3].lower, infinite.issues[3].upper) == (-np.inf, np.inf)
    assert infinite.issued_evaluation_origins == (3, 4)


def test_common_evaluation_mask_includes_infinite_intervals_and_failed_dates():
    baseline = run_rolling_prequential([1] * 9, fixed_forecast,
                                       config(window=3, alpha=0.05, method="base"))

    def fails_at_four(history):
        if len(history) == 4:
            raise ArithmeticError("fit failure")
        return fixed_forecast(history)

    failed = run_rolling_prequential([1] * 9, fails_at_four,
                                     config(window=3, alpha=0.05, method="failed"))
    assert common_evaluation_origins(baseline, failed) == (3, 4, 5, 6, 7, 8)
    assert failed.issued_evaluation_origins == (3, 8)
    assert baseline.issues[4].status == "issued"
    assert failed.issues[4].status == "fit_failed"


def test_common_evaluation_mask_rejects_different_response_paths():
    first = run_rolling_prequential([1] * 5, fixed_forecast, config())
    second = run_rolling_prequential([1, 1, 1, 1, 2], fixed_forecast, config())
    with pytest.raises(ValueError, match="same response sequence"):
        common_evaluation_origins(first, second)


def test_common_evaluation_mask_requires_predeclared_shared_start():
    first = run_rolling_prequential([1] * 6, fixed_forecast, config())
    second = run_rolling_prequential([1] * 6, fixed_forecast,
                                     config(evaluation_start=4, method="later"))
    with pytest.raises(ValueError, match="predeclared evaluation_start"):
        common_evaluation_origins(first, second)


@pytest.mark.parametrize("factor", [0.3, 7.0])
def test_unit_equivariance_of_prequential_intervals(factor):
    y = [1.0, -3.0, 2.0, -4.0, 5.0]

    def forecast_at_scale(scale):
        return lambda history: Forecast(0.0, scale, len(history) - 1)

    base = run_rolling_prequential(y, forecast_at_scale(1.0), config())
    scaled = run_rolling_prequential([factor * value for value in y],
                                    forecast_at_scale(factor), config())
    for origin in base.issued_evaluation_origins:
        assert scaled.issues[origin].upper == pytest.approx(factor * base.issues[origin].upper)
        assert scaled.issues[origin].lower == pytest.approx(factor * base.issues[origin].lower)


def test_constant_multiplicative_scale_bias_cancels_pathwise():
    y = [1.0, -3.0, 2.0, -4.0, 5.0]
    base = run_rolling_prequential(y, lambda h: Forecast(0, 1, len(h) - 1), config())
    biased = run_rolling_prequential(y, lambda h: Forecast(0, 4, len(h) - 1), config())
    for origin in base.issued_evaluation_origins:
        assert (base.issues[origin].lower, base.issues[origin].upper) == (
            biased.issues[origin].lower, biased.issues[origin].upper)


@pytest.mark.parametrize("bad", [
    {"window": 0}, {"window": 2.5}, {"alpha": 0}, {"alpha": 1},
    {"alpha": float("nan")}, {"evaluation_start": 2},
])
def test_invalid_protocol_config_rejected(bad):
    values = {"method": "rolling", "window": 3, "alpha": 0.5, "evaluation_start": 3}
    values.update(bad)
    with pytest.raises(ValueError):
        RollingConfig(**values)


def test_invalid_scale_is_visible_without_losing_later_dates():
    def bad_once(history):
        if len(history) == 2:
            return Forecast(0.0, 0.0, 1)
        return fixed_forecast(history)

    result = run_rolling_prequential([1] * 7, bad_once, config())
    assert result.issues[2].status == "invalid_forecast"
    assert result.issues[2].failure_type == "NonfiniteOrNonpositiveEstimate"
    assert result.revealed[2].vintage_score is None
    assert result.issues[6].status == "issued"


def test_nonfinite_outcome_is_rejected_at_reveal_and_matrix_input_is_rejected():
    seen = []

    def forecaster(history):
        seen.append(history)
        return fixed_forecast(history)

    with pytest.raises(ValueError, match="origin 3"):
        run_rolling_prequential([1, 2, 3, float("nan")], forecaster, config())
    assert seen[-1] == (1.0, 2.0, 3.0)
    with pytest.raises(ValueError, match="one-dimensional"):
        run_rolling_prequential(np.ones((4, 1)), forecaster, config())
    with pytest.raises(ValueError, match="after evaluation_start"):
        run_rolling_prequential([1, 2, 3], forecaster, config())
