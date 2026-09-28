"""A minimal forecast-before-reveal protocol for fixed-window intervals.

This module implements only symmetric, vintage-score rolling calibration.  It
does not implement ACI, SPCI, or a coverage guarantee under dependence.  A
forecaster receives an immutable prefix of observed responses; simulation
truth (such as the current volatility or a change point) is never passed to a
deployable forecaster by this API.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
import math
from numbers import Integral, Real
from typing import Literal


class ProtocolViolation(ValueError):
    """A forecast claims to use unavailable data or has an invalid cutoff."""


@dataclass(frozen=True)
class Forecast:
    """A prediction fixed before response ``origin`` is revealed.

    ``fit_cutoff`` is the last outcome index used for model fitting.  Use -1
    for a fixed prior; a periodically refitted model may have an older cutoff.
    """

    mu_hat: float
    sigma_hat: float
    fit_cutoff: int


@dataclass(frozen=True)
class RollingConfig:
    method: str
    window: int
    alpha: float
    evaluation_start: int

    def __post_init__(self) -> None:
        if not isinstance(self.method, str) or not self.method.strip():
            raise ValueError("method must be nonempty")
        if isinstance(self.window, bool) or not isinstance(self.window, Integral) or self.window < 1:
            raise ValueError("window must be a positive integer")
        if (isinstance(self.alpha, bool) or not isinstance(self.alpha, Real)
                or not math.isfinite(self.alpha) or not 0 < self.alpha < 1):
            raise ValueError("alpha must be strictly between zero and one")
        if (isinstance(self.evaluation_start, bool)
                or not isinstance(self.evaluation_start, Integral)
                or self.evaluation_start < self.window):
            raise ValueError("evaluation_start must be at least window")

    @property
    def rank(self) -> int:
        return math.ceil((self.window + 1) * (1 - self.alpha))


IssueStatus = Literal[
    "issued", "warmup", "insufficient_calibration", "fit_failed",
    "invalid_forecast", "numerical_failure",
]


@dataclass(frozen=True)
class IssuedInterval:
    """Saved before observing ``Y_origin``; None bounds mean no interval."""

    origin: int
    method: str
    status: IssueStatus
    fit_cutoff: int | None
    mu_hat: float | None
    sigma_hat: float | None
    calibration_count: int
    rank: int
    lower: float | None
    upper: float | None
    failure_type: str | None = None


ScoreStatus = Literal["scored", "unscored_forecast", "nonfinite_score"]


@dataclass(frozen=True)
class RevealedOutcome:
    """The stored score uses the estimates in the same-origin issue record."""

    origin: int
    outcome: float
    vintage_score: float | None
    status: ScoreStatus


@dataclass(frozen=True)
class PrequentialResult:
    config: RollingConfig
    issues: tuple[IssuedInterval, ...]
    revealed: tuple[RevealedOutcome, ...]

    @property
    def planned_evaluation_origins(self) -> tuple[int, ...]:
        """All predeclared evaluation dates, including failures."""
        return tuple(range(self.config.evaluation_start, len(self.issues)))

    @property
    def issued_evaluation_origins(self) -> tuple[int, ...]:
        """Dates with issued intervals, including infinite intervals."""
        return tuple(issue.origin for issue in self.issues
                     if issue.origin >= self.config.evaluation_start
                     and issue.status == "issued")


def common_evaluation_origins(*results: PrequentialResult) -> tuple[int, ...]:
    """Common *planned* dates, never silently dropping a failed prediction.

    Report method failures on these dates alongside any metric that is defined
    only for issued intervals.  Infinite intervals remain issued intervals.
    """
    if not results:
        raise ValueError("at least one result is required")
    lengths = {len(result.issues) for result in results}
    if len(lengths) != 1:
        raise ValueError("methods must have the same number of origins")
    starts = {result.config.evaluation_start for result in results}
    if len(starts) != 1:
        raise ValueError("methods must use the same predeclared evaluation_start")
    outcomes = tuple(row.outcome for row in results[0].revealed)
    if any(tuple(row.outcome for row in result.revealed) != outcomes
           for result in results[1:]):
        raise ValueError("methods must use the same response sequence")
    shared = set(results[0].planned_evaluation_origins)
    for result in results[1:]:
        shared.intersection_update(result.planned_evaluation_origins)
    return tuple(sorted(shared))


def _forecast_error(forecast: Forecast, origin: int) -> str | None:
    if not isinstance(forecast, Forecast):
        raise TypeError("forecaster must return Forecast")
    cutoff = forecast.fit_cutoff
    if isinstance(cutoff, bool) or not isinstance(cutoff, Integral) or cutoff < -1 or cutoff >= origin:
        raise ProtocolViolation(f"fit_cutoff must lie in [-1, {origin - 1}] at origin {origin}")
    if (isinstance(forecast.mu_hat, bool) or not isinstance(forecast.mu_hat, Real)
            or isinstance(forecast.sigma_hat, bool) or not isinstance(forecast.sigma_hat, Real)
            or not math.isfinite(forecast.mu_hat)
            or not math.isfinite(forecast.sigma_hat)
            or forecast.sigma_hat <= 0):
        return "NonfiniteOrNonpositiveEstimate"
    return None


def run_rolling_prequential(
    outcomes: Sequence[float],
    forecaster: Callable[[tuple[float, ...]], Forecast],
    config: RollingConfig,
) -> PrequentialResult:
    """Issue at ``t`` from data ``<t``; reveal, score, then advance to ``t+1``.

    A missing fit or score occupies its original time slot.  The age-based
    window is ``[t-window, t)``; older scores are never pulled forward to fill
    holes.  Failed forecasts are recorded with their exception class, without
    copying potentially sensitive exception messages into a research trace.

    A forecaster should be pure or freshly initialized for each run.  This API
    withholds future outcomes and oracle fields from its arguments, but cannot
    inspect arbitrary data captured by a Python closure.
    """
    if len(outcomes) == 0 or getattr(outcomes, "ndim", 1) != 1:
        raise ValueError("outcomes must be a nonempty one-dimensional sequence")
    if len(outcomes) <= config.evaluation_start:
        raise ValueError("outcomes must contain an origin after evaluation_start")

    history: tuple[float, ...] = ()
    issues: list[IssuedInterval] = []
    revealed: list[RevealedOutcome] = []
    k = config.rank
    for t in range(len(outcomes)):
        eligible = [row.vintage_score for row in revealed[max(0, t - config.window):t]
                    if row.vintage_score is not None]
        count = len(eligible)
        forecast: Forecast | None = None
        failure_type: str | None = None
        try:
            forecast = forecaster(history)
        except ProtocolViolation:
            raise
        except Exception as exc:
            failure_type = type(exc).__name__

        if failure_type is not None:
            status: IssueStatus = "fit_failed"
        elif forecast is None:
            status = "invalid_forecast"
            failure_type = "MissingForecast"
        else:
            error = _forecast_error(forecast, t)
            if error is not None:
                status = "invalid_forecast"
                failure_type = error
                forecast = None
            elif t < config.window:
                status = "warmup"
            elif count < config.window:
                status = "insufficient_calibration"
            else:
                status = "issued"

        lower: float | None = None
        upper: float | None = None
        if status == "issued":
            assert forecast is not None
            if k > config.window:
                lower, upper = -math.inf, math.inf
            else:
                q = sorted(eligible)[k - 1]
                radius = forecast.sigma_hat * q
                lower, upper = forecast.mu_hat - radius, forecast.mu_hat + radius
                if not math.isfinite(radius) or not all(map(math.isfinite, (lower, upper))):
                    status = "numerical_failure"
                    failure_type = "IntervalOverflow"
                    lower, upper = None, None

        # Store the interval (or explicit failure) before revealing y_t.
        issues.append(IssuedInterval(
            origin=t, method=config.method, status=status,
            fit_cutoff=forecast.fit_cutoff if forecast is not None else None,
            mu_hat=forecast.mu_hat if forecast is not None else None,
            sigma_hat=forecast.sigma_hat if forecast is not None else None,
            calibration_count=count, rank=k, lower=lower, upper=upper,
            failure_type=failure_type,
        ))

        # Reveal only now.  In particular, a forecaster never receives or
        # reads Y_t through this function before its interval is recorded.
        raw_y_t = outcomes[t]
        if isinstance(raw_y_t, bool) or not isinstance(raw_y_t, Real):
            raise ValueError(f"outcome at origin {t} must be a finite scalar")
        y_t = float(raw_y_t)
        if not math.isfinite(y_t):
            raise ValueError(f"outcome at origin {t} must be finite")
        if forecast is None:
            revealed.append(RevealedOutcome(t, y_t, None, "unscored_forecast"))
        else:
            score = abs(y_t - forecast.mu_hat) / forecast.sigma_hat
            if math.isfinite(score):
                revealed.append(RevealedOutcome(t, y_t, score, "scored"))
            else:
                revealed.append(RevealedOutcome(t, y_t, None, "nonfinite_score"))
        history += (y_t,)

    return PrequentialResult(config, tuple(issues), tuple(revealed))
