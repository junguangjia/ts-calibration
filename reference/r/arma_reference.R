# Classical ARIMA reference for a predeclared order. This is not an online
# calibration method. Origin is the one-based index of the forecasted outcome.
fit_arima_prefix <- function(y, origin, order = c(1L, 0L, 0L),
                             include_mean = FALSE) {
  if (!is.numeric(y) || !is.null(dim(y))) {
    stop("y must be a numeric vector")
  }
  if (!is.numeric(origin) || length(origin) != 1L || !is.finite(origin) ||
      origin != as.integer(origin) || origin < 2L ||
      origin > length(y) + 1L) {
    stop("origin must be a valid one-based forecast index")
  }
  if (!is.numeric(order) || !is.null(dim(order)) || length(order) != 3L ||
      any(!is.finite(order)) ||
      any(order != as.integer(order)) || any(order < 0L)) {
    stop("order must contain three nonnegative integers")
  }
  if (length(include_mean) != 1L || is.na(include_mean) ||
      !is.logical(include_mean)) {
    stop("include_mean must be TRUE or FALSE")
  }
  if (order[2L] > 0L && include_mean) {
    stop("include_mean is only defined here for undifferenced ARMA fits")
  }

  fit_cutoff <- as.integer(origin) - 1L
  train <- y[seq_len(fit_cutoff)]
  if (fit_cutoff < max(30L, sum(order) + 10L) || any(!is.finite(train))) {
    stop("training prefix is too short or contains nonfinite values")
  }

  fit <- stats::arima(train, order = as.integer(order),
                      include.mean = include_mean, method = "ML")
  if (fit$code != 0L) stop("ARIMA optimization did not converge")
  next_step <- stats::predict(fit, n.ahead = 1L)
  list(
    origin = as.integer(origin),
    fit_cutoff = fit_cutoff,
    order = as.integer(order),
    include_mean = include_mean,
    mu_hat = as.numeric(next_step$pred[1L]),
    forecast_se = as.numeric(next_step$se[1L]),
    aic = as.numeric(stats::AIC(fit)),
    optimizer_convergence = fit$code,
    coefficients = fit$coef,
    innovation_variance = as.numeric(fit$sigma2),
    # Retrospective in-sample residuals; never use these as vintage scores.
    fitted_residuals = as.numeric(stats::residuals(fit))
  )
}
