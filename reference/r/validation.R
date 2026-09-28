# Small deterministic smoke check for the independent classical R reference.
# Usage: Rscript reference/r/validation.R results/<new-run-id>
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L || !nzchar(args[1L])) {
  stop("supply one NEW output directory under results/")
}
file_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
if (length(file_arg) != 1L) stop("run validation.R with Rscript")
script_dir <- dirname(normalizePath(sub("^--file=", "", file_arg)))
project_root <- dirname(dirname(script_dir))
result_root <- file.path(project_root, "results")
dir.create(result_root, showWarnings = FALSE)
if (!identical(normalizePath(dirname(args[1L])), normalizePath(result_root)) ||
    file.exists(args[1L])) {
  stop("output must be a fresh direct child of results/")
}

source(file.path(script_dir, "arma_reference.R"))
source(file.path(script_dir, "garch_reference.R"))
source(file.path(script_dir, "diagnostics.R"))

set.seed(5221)
arma_y <- as.numeric(stats::arima.sim(n = 500L,
                                     model = list(ar = 0.50, ma = -0.20)))
arma_origin <- 401L
arma_fit <- fit_arima_prefix(arma_y, arma_origin, c(1L, 0L, 1L))
arma_suffix_changed <- arma_y
arma_suffix_changed[arma_origin:length(arma_y)] <- NA_real_
arma_recheck <- fit_arima_prefix(arma_suffix_changed, arma_origin,
                                c(1L, 0L, 1L))
stopifnot(arma_fit$fit_cutoff == arma_origin - 1L,
          identical(arma_fit$mu_hat, arma_recheck$mu_hat),
          identical(arma_fit$forecast_se, arma_recheck$forecast_se),
          identical(arma_fit$coefficients, arma_recheck$coefficients),
          is.finite(arma_fit$mu_hat), arma_fit$forecast_se > 0)
arma_diag <- residual_diagnostics(
  arma_fit$fitted_residuals / sqrt(arma_fit$innovation_variance),
  lag = 10L, fitdf = 2L)

# Stable GARCH fixture with known zero conditional mean and a fixed burn-in.
# The fit sees only innovations[1:(origin-1)] and never the current outcome.
n_sim <- 700L
z <- stats::rnorm(n_sim)
h <- numeric(n_sim)
x <- numeric(n_sim)
h[1L] <- 1
x[1L] <- sqrt(h[1L]) * z[1L]
for (i in 2L:n_sim) {
  h[i] <- 0.08 + 0.07 * x[i - 1L]^2 + 0.85 * h[i - 1L]
  x[i] <- sqrt(h[i]) * z[i]
}
garch_x <- x[101L:n_sim]
garch_origin <- 401L
garch_fit <- fit_garch11_prefix(garch_x, garch_origin)
garch_suffix_changed <- garch_x
garch_suffix_changed[garch_origin:length(garch_x)] <- NA_real_
garch_recheck <- fit_garch11_prefix(garch_suffix_changed, garch_origin)
stopifnot(garch_fit$fit_cutoff == garch_origin - 1L,
          identical(garch_fit$sigma_hat, garch_recheck$sigma_hat),
          identical(garch_fit$omega, garch_recheck$omega),
          identical(garch_fit$alpha, garch_recheck$alpha),
          identical(garch_fit$beta, garch_recheck$beta),
          garch_fit$omega > 0, garch_fit$alpha > 0, garch_fit$beta > 0,
          garch_fit$alpha + garch_fit$beta < 1,
          is.finite(garch_fit$sigma_hat), garch_fit$sigma_hat > 0)
garch_diag <- residual_diagnostics(garch_fit$fitted_standardized_residuals,
                                   lag = 10L)
stopifnot(all(is.finite(unlist(arma_diag))),
          all(is.finite(unlist(garch_diag))))

dir.create(args[1L], showWarnings = FALSE)
if (!dir.exists(args[1L])) stop("could not create output directory")
configuration <- c(
  experiment_status = "development_smoke",
  seed = "5221",
  arma_dgp = "ARMA(1,1): ar=0.50, ma=-0.20, innovation_sd=1",
  arma_n = "500",
  arma_fit_order = "(1,0,1)",
  arma_origin = as.character(arma_origin),
  garch_dgp = "GARCH(1,1): omega=0.08, alpha=0.07, beta=0.85, zero_mean",
  garch_n_before_burnin = as.character(n_sim),
  garch_burnin = "100",
  garch_origin_after_burnin = as.character(garch_origin),
  garch_fit = "base-R Gaussian QMLE, stationary interior"
)
utils::write.csv(data.frame(setting = names(configuration),
                            value = unname(configuration)),
                 file.path(args[1L], "config.csv"), row.names = FALSE)
values <- c(
  arma_origin = arma_origin,
  arma_fit_cutoff = arma_fit$fit_cutoff,
  arma_forecast_mean = arma_fit$mu_hat,
  arma_forecast_se = arma_fit$forecast_se,
  arma_aic = arma_fit$aic,
  arma_optimizer_convergence = arma_fit$optimizer_convergence,
  arma_ljung_box_p = arma_diag$ljung_box_p,
  arma_ljung_box_squared_p = arma_diag$ljung_box_squared_p,
  arma_arch_lm_p = arma_diag$arch_lm_p,
  garch_origin = garch_origin,
  garch_fit_cutoff = garch_fit$fit_cutoff,
  garch_omega = garch_fit$omega,
  garch_alpha = garch_fit$alpha,
  garch_beta = garch_fit$beta,
  garch_forecast_sigma = garch_fit$sigma_hat,
  garch_optimizer_convergence = garch_fit$optimizer_convergence,
  garch_at_parameter_bound = as.integer(garch_fit$at_parameter_bound),
  garch_ljung_box_p = garch_diag$ljung_box_p,
  garch_ljung_box_squared_p = garch_diag$ljung_box_squared_p,
  garch_arch_lm_p = garch_diag$arch_lm_p,
  current_and_future_mutation_invariance = 1L
)
utils::write.csv(data.frame(metric = names(values), value = unname(values)),
                 file.path(args[1L], "validation.csv"), row.names = FALSE)
source_files <- file.path(script_dir, c("arma_reference.R", "garch_reference.R",
                                        "diagnostics.R", "validation.R"))
utils::write.csv(data.frame(file = basename(source_files),
                            md5 = unname(tools::md5sum(source_files))),
                 file.path(args[1L], "source_md5.csv"), row.names = FALSE)
utils::write.csv(data.frame(model = "garch11_qmle",
                            convergence = garch_fit$optimizer_convergence,
                            at_parameter_bound = garch_fit$at_parameter_bound,
                            optimizer_message = garch_fit$optimizer_message),
                 file.path(args[1L], "fit_status.csv"), row.names = FALSE)
writeLines(c("Seed: 5221", "ARIMA: stats::arima ML, order (1,0,1)",
             "GARCH: local base-R Gaussian QMLE, stationary interior constraint",
             "No external GARCH package was used.",
             paste0("stats package: ", utils::packageVersion("stats")),
             paste0("utils package: ", utils::packageVersion("utils")),
             paste0("tools package: ", utils::packageVersion("tools")),
             "", capture.output(sessionInfo())),
           file.path(args[1L], "session.txt"))
cat("R classical reference validation passed:", args[1L], "\n")
