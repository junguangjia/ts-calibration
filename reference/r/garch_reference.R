# Independent base-R Gaussian QMLE reference for zero-mean GARCH(1,1).
# It is not a package-authoritative fit and does not represent the IGARCH
# alpha + beta = 1 boundary used in legacy HW5. Origin is one-based.
fit_garch11_prefix <- function(innovations, origin) {
  if (!is.numeric(innovations) || !is.null(dim(innovations))) {
    stop("innovations must be a numeric vector")
  }
  if (!is.numeric(origin) || length(origin) != 1L || !is.finite(origin) ||
      origin != as.integer(origin) || origin < 2L ||
      origin > length(innovations) + 1L) {
    stop("origin must be a valid one-based forecast index")
  }
  fit_cutoff <- as.integer(origin) - 1L
  x <- innovations[seq_len(fit_cutoff)]
  if (fit_cutoff < 80L || any(!is.finite(x)) ||
      !is.finite(stats::var(x)) || stats::var(x) <= 0) {
    stop("training prefix needs at least 80 finite, nonconstant values")
  }

  sample_variance <- mean(x^2)
  # The bounded transform enforces omega > 0, alpha > 0, beta > 0,
  # alpha + beta < 1. This excludes the legacy alpha + beta = 1 stress case.
  unpack <- function(theta) {
    alpha <- stats::plogis(theta[2L])
    beta <- (1 - alpha) * stats::plogis(theta[3L])
    c(omega = exp(theta[1L]), alpha = alpha, beta = beta)
  }
  filter_variance <- function(par) {
    h <- numeric(fit_cutoff)
    h[1L] <- sample_variance
    if (fit_cutoff > 1L) {
      for (i in 2L:fit_cutoff) {
        h[i] <- par["omega"] + par["alpha"] * x[i - 1L]^2 +
          par["beta"] * h[i - 1L]
      }
    }
    h
  }
  neg_log_likelihood <- function(theta) {
    h <- filter_variance(unpack(theta))
    if (any(!is.finite(h)) || any(h <= 0)) return(.Machine$double.xmax)
    0.5 * sum(log(2 * pi) + log(h) + x^2 / h)
  }

  lower <- c(log(sample_variance * 1e-8), -12, -12)
  upper <- c(log(sample_variance * 1e3), 12, 12)
  initial <- c(log(sample_variance * 0.05), stats::qlogis(0.05),
               stats::qlogis(0.90 / 0.95))
  opt <- stats::optim(initial, neg_log_likelihood, method = "L-BFGS-B",
                      lower = lower, upper = upper,
                      control = list(maxit = 1000L))
  if (opt$convergence != 0L || !is.finite(opt$value)) {
    stop(sprintf("GARCH optimization failed: code %d; %s",
                 opt$convergence, opt$message))
  }
  par <- unpack(opt$par)
  h <- filter_variance(par)
  h_next <- unname(par["omega"] + par["alpha"] * x[fit_cutoff]^2 +
                     par["beta"] * h[fit_cutoff])
  if (!is.finite(h_next) || h_next <= 0) stop("invalid GARCH forecast")
  at_bound <- any(abs(opt$par - lower) < 1e-5 |
                    abs(opt$par - upper) < 1e-5)

  list(
    origin = as.integer(origin),
    fit_cutoff = fit_cutoff,
    omega = unname(par["omega"]),
    alpha = unname(par["alpha"]),
    beta = unname(par["beta"]),
    variance_hat = h_next,
    sigma_hat = sqrt(h_next),
    log_likelihood = -opt$value,
    optimizer_convergence = opt$convergence,
    optimizer_message = opt$message,
    at_parameter_bound = at_bound,
    # Retrospective full-prefix residuals; never use as vintage scores.
    fitted_standardized_residuals = x / sqrt(h)
  )
}
