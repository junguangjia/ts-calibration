# Descriptive diagnostics of a supplied residual sequence. P-values rely on
# large-sample approximations and do not establish model adequacy.
residual_diagnostics <- function(z, lag = 10L, fitdf = 0L) {
  if (!is.numeric(z) || !is.null(dim(z)) || any(!is.finite(z))) {
    stop("z must be a finite numeric vector")
  }
  if (!is.numeric(lag) || length(lag) != 1L || !is.finite(lag) ||
      lag != as.integer(lag) ||
      lag < 1L || lag >= length(z) - 5L) {
    stop("lag must be a positive integer with enough residuals")
  }
  if (!is.numeric(fitdf) || length(fitdf) != 1L || !is.finite(fitdf) ||
      fitdf != as.integer(fitdf) || fitdf < 0L || fitdf >= lag) {
    stop("fitdf must be a nonnegative integer smaller than lag")
  }
  lb <- stats::Box.test(z, lag = lag, type = "Ljung-Box", fitdf = fitdf)
  lb_squared <- stats::Box.test(z^2, lag = lag, type = "Ljung-Box")
  embedded <- embed(z^2, lag + 1L)
  arch_fit <- stats::lm(embedded[, 1L] ~ embedded[, -1L, drop = FALSE])
  arch_lm <- nrow(embedded) * summary(arch_fit)$r.squared
  list(
    n = length(z), lag = as.integer(lag), fitdf = as.integer(fitdf),
    ljung_box_p = unname(lb$p.value),
    ljung_box_squared_p = unname(lb_squared$p.value),
    arch_lm_statistic = unname(arch_lm),
    arch_lm_p = stats::pchisq(arch_lm, df = lag, lower.tail = FALSE)
  )
}
