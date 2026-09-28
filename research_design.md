# Research design v1: Volatility-estimation lag and calibration memory

Prepared for Junguang Jia, 2026-09-28 UTC (2026-09-27 in New York).
Status: research-feasibility design, with an exploratory mechanism pilot and numerical checks of elementary mathematical claims. This is not a finished research paper or a verified novelty claim.

## 1. Proposed research question

**When does volatility normalization improve sequential prediction intervals, and when do historical scale-estimation errors persist through the calibration window after the scale forecast has recovered?**

Working title: **Volatility-Estimation Lag and Calibration Memory in Sequential Prediction Intervals**.

The initial application is one-step-ahead prediction of a scalar response with time-varying conditional scale. The principal target is the NEXT RESPONSE, not a confidence interval for a parameter, a prediction of realized volatility, a trading return, or an investment strategy. Begin with a known zero conditional mean. Later add the same causal estimated mean forecast to every interval method.

The prospective contribution is a precise account of a transient mechanism, its finite-window consequences, and the conditions under which it matters in realistic scale forecasts. A new algorithm is optional. Adding GARCH normalization to conformal prediction is NOT new. Reporting that overall coverage can conceal local failures is NOT new.

Do not call the selected question settled until its novelty and technical correctness have been independently checked against the full papers listed below.

## 2. What was actually checked

The two original Rmd files were reviewed in full. HW4 contains AR/MA order-selection simulations and in-sample IBM ARMA fitting/diagnostics. HW5 contains one 300-observation GARCH simulation, a full-series fit, and diagnostic discussion. They do not yet implement a chronological forecast-calibrate-update experiment. Original files were not modified or executed.

The original HW5 uses omega=5, a=b=0.5. Thus a+b=1 is a finite-second-moment boundary, not an ordinary covariance-stationary GARCH design. Do not infer that strict stationarity is impossible; that is a different condition. Preserve this case as an explicitly labeled stress test, not the main experiment.

The IBM CSV preview contains an index and a value column (`"","x"`), without a date field. It must not be presented as recent market data or assigned crisis dates until provenance is recovered. Use it as a legacy smoke test first.

The following scripts were executed in a separate reference environment:
- `pilot.py`: 200 independent Gaussian scale-jump paths, causal EWMA and rolling quantile methods; all results are exploratory.
- `theory_checks.py`: numerical integration and 40,000 independent Monte Carlo draws per configuration to check the finite-window identity below.

No SPCI, ACI, SAOCP, PID, fitted GARCH, or proposed window-switching method was tested in this pilot. The pilot is not a comparison against the state of the art.

## 3. Source provenance

The original HW4/HW5 Rmd files, assignment sheets, reports, and IBM CSV were
reviewed as private source material. They originate in Columbia STAT 5221,
Time Series Analysis, and are not redistributed here. Do not present instructor
problem sheets or solutions as original research code. The IBM series has no
verified dates or source license for research redistribution.

## 4. Literature map and novelty boundaries

[R1] Gibbs and Candes. Adaptive Conformal Inference Under Distribution Shift. NeurIPS 2021.
https://arxiv.org/abs/2106.00170
https://arxiv.org/html/2106.00170v3
Read especially Sections 2.2, 4.1, and 5. The paper already uses GARCH-normalized scores for a realized-volatility target, studies the effect of normalization, and provides a pathwise long-run coverage-frequency result under its stated update and extended-quantile conventions. Its target is not identical to our response/return interval target. Neither that difference nor changing the dataset is sufficient novelty.

[R2] Xu and Xie. Sequential Predictive Conformal Inference for Time Series. ICML 2023.
https://proceedings.mlr.press/v202/xu23r.html
https://proceedings.mlr.press/v202/xu23r/xu23r.pdf
SPCI predicts conditional quantiles of future residuals/scores using temporal dependence. Its conditional coverage statement is asymptotic and assumption-dependent. It is not an exact finite-sample, arbitrary-process conditional-coverage guarantee. Verify Appendix A's assumptions and reproduce the actual algorithm, not a vaguely similar rolling quantile method.

[R3] Bhatnagar, Wang, Xiong, and Bai. Improved Online Conformal Prediction via Strongly Adaptive Online Learning. ICML 2023.
https://proceedings.mlr.press/v202/bhatnagar23a.html
Author implementation: https://github.com/salesforce/online_conformal
Multiple calibration experts, adaptivity across time intervals, and adaptive regret are prior art. Record any required score/radius bounds, initialization, and tuning assumptions.

[R4] Angelopoulos, Candes, and Tibshirani. Conformal PID Control for Time Series Prediction. NeurIPS 2023.
https://arxiv.org/abs/2307.16895
Author implementation: https://github.com/aangelopoulos/conformal-time-series
Quantile tracking, error integration, and prospective scorecasting are prior art. "Prediction plus a feedback controller" is not a new contribution by itself.

[R5] Barber, Candes, Ramdas, and Tibshirani. Conformal prediction beyond exchangeability. Annals of Statistics 2023.
https://arxiv.org/abs/2202.13415
Weighted calibration and coverage-gap analysis under distribution drift are established. Simple empirical-CDF-plus-drift decompositions need comparison against this literature before being called new.

[R6] Aich, Aich, and Jain. Temporal Conformal Prediction (TCP): Rolling Calibration for Financial Risk Forecasting. arXiv:2507.05470, version 7, 2026-09-20.
https://arxiv.org/abs/2507.05470v7
The current abstract describes rolling CQR-related procedures, volatility-based comparators, and differences between coverage and interval-score conclusions. Earlier indexed abstracts have different titles and more favorable summaries. Use the actual version read, and label this as a preprint. Full experimental reproduction has not been performed here.

[R7] Oancea. Dynamic Regime-Aware Conformal Calibration for Reliable Economic Forecast Intervals under Multiple Distribution Shifts. arXiv:2608.17079, 2026-08-17.
https://arxiv.org/abs/2608.17079
https://arxiv.org/html/2608.17079v1
A relevant preprint combining regime-aware weighting and online calibration; its abstract explicitly discusses conditional-scale normalization and controller ablations. Treat its empirical/theoretical claims as author claims pending detailed verification, not as settled external facts or a required full implementation in the first pilot.

[R8] El Halabi and Brandt. Adaptive Conformal Inference Under Delayed Feedback: Coverage Guarantees and a Delay-to-Memory Diagnostic. arXiv:2609.07251, indexed as 2026-09-07.
https://arxiv.org/abs/2609.07251
An indexed abstract was retrieved, but the abstract page and full text were not available for review. It discusses residual persistence, GARCH/Markov switching, normalization, and abrupt shifts. Full text MUST be checked before claiming a novel delay/memory diagnostic. This project's first version deliberately uses horizon 1, not delayed-feedback theory.

Access level matters: R1 was inspected in full HTML at the relevant sections; R2's method/theory and assumptions were inspected; R3-R5 were verified at the paper/author-source level; R6-R7 provide current overlapping preprint evidence but were not comprehensively audited; R8 is an abstract-level lead with an access limitation. Do not write that all eight papers were fully reviewed.

Future literature review must extend this map with targeted searches for scale-normalized conformal prediction, volatility-normalized residuals, score vintage, transient scale estimation, calibration memory, adaptive windows, delayed scale recovery, studentization, and tail-shape drift. Save the search date, paper version, theorem/section, code commit and unresolved access limitations. Use primary papers and authors' repositories rather than secondary summaries.

## 5. Formal setup and coverage targets

Let F_(t-1) contain the observed data and algorithm randomness available before observing Y_t. Every forecast, scale, window choice, and interval at t must be measurable with respect to F_(t-1).

Start with

    Y_t = mu_t + sigma_t Z_t,
    Z_t independent of F_(t-1), E Z_t = 0, E Z_t^2 = 1,
    sigma_t > 0 and predictable under the model.

Begin with mu_t known to be zero. The variance-one convention identifies sigma_t as conditional standard deviation, rather than an arbitrary rescaling of Z_t. For a latent stochastic-volatility stress test, conditioning on the hidden sigma_t is a latent-state diagnostic, NOT automatically coverage conditional on the observable history.

Let muhat_t and sigmahat_t be causal forecasts. Store the VINTAGE score after Y_t is observed:

    R_t = |Y_t - muhat_t| / sigmahat_t.

For a fixed window W and p=1-alpha, let k=ceil((W+1)*p) and q_t be the kth order statistic of R_(t-W),...,R_(t-1). If k>W, the corrected threshold is infinity; never silently replace it by the sample maximum. Define

    I_t = [muhat_t - sigmahat_t q_t, muhat_t + sigmahat_t q_t].

Historical scores use their original pre-outcome predictions. Do not recompute R_i using a model fit on Y_i or later observations and present the result as the same prequential algorithm. Honest retrospective cross-fitting would be a different method with different theory.

Distinguish:
1. Unconditional/marginal coverage at an origin, averaging over histories and the next outcome.
2. Long-run empirical coverage over time.
3. Observable-history conditional coverage P(Y_t in I_t | F_(t-1)).
4. Event-window/state-stratified empirical diagnostics.

Good performance on (2) or (4) does not prove (3). Adjacent rolling-window summaries are not independent observations. An oracle scale with iid innovations gives the familiar marginal rank coverage k/(W+1) at a fixed origin; conditional coverage given the realized calibration sample still fluctuates.

The rank correction does not create exchangeability for estimated, adaptive time-series scores. Every guarantee must name its assumptions.

## 6. Testable hypotheses, including ways they can fail

H1: With stable innovation shape, scale normalization usually reduces score drift caused by changing volatility. This qualitative idea is established; use it as a baseline, not novelty.

H2: With finite-window VINTAGE calibration, a transient scale-forecast error can outlive the scale error itself. Early underestimated scale inflates past scores, which can inflate later widths after scale recovery. Early overestimated scale can produce the opposite phenomenon. Quantify duration and size, rather than just plotting it.

H3: The relevant quantity is variation in RELATIVE scale error across the calibration window, not the absolute magnitude of sigma_t, nor absolute scale-estimation error by itself.

H4: There is no universally best short calibration window: faster adaptation competes with quantile estimation noise and finite-rank effects. Claims about window choice must survive matched rank conventions and locked tuning.

H5: Shape changes at fixed variance are not removed by scale normalization. An algorithm that discards large scores as if they were estimation mistakes can fail badly when they represent a genuine tail change.

Falsification targets: H2 might be negligible under realistic scale estimators, already fully characterized in prior work, or no better explained by the proposed diagnostics than by ordinary score drift. A candidate window adaptation may offer no gain over fixed short windows, ACI, SPCI, SAOCP or PID. Report these outcomes rather than adding increasingly complex components until a win appears.

## 7. Mathematical building blocks derived for this design

These are elementary results developed here for framing and testing. Correct derivation does NOT establish originality or publication-level contribution. The proofs require independent review and comparison with prior art.

### 7.1 Constant multiplicative scale bias cancels exactly

With the true mean, suppose sigmahat_i=c sigma_i for ALL calibration observations and the current prediction, with fixed c>0. Then R_i=|Z_i|/c and q_t=Q_t(|Z|)/c. Consequently,

    sigmahat_t q_t = sigma_t Q_t(|Z|).

The entire interval is identical to its oracle-scale rolling counterpart, pathwise. Thus scale RMSE alone cannot diagnose interval calibration. A scale estimator with a stable multiplicative bias can give exactly the same intervals as the oracle-scale procedure. A data-dependent changing c_i is different.

### 7.2 Fixed-window error decomposition

Assume muhat_t=mu_t, iid continuous Z_t, and let G be the CDF of |Z| with density g. Define

    eta_i = log(sigmahat_i / sigma_i),
    H_i(x) = P(R_i <= x | F_(i-1)) = G(exp(eta_i) x),
    Hbar_t(x) = (1/W) sum_(i=t-W)^(t-1) H_i(x),
    Hhat_t(x) = (1/W) sum_(i=t-W)^(t-1) 1{R_i <= x}.

Since q_t is past-measurable, the actual conditional coverage is

    c_t = G(exp(eta_t) q_t).

For distinct scores and k<=W, Hhat_t(q_t)=k/W. The triangle inequality gives the PATHWISE bound

    |c_t-p| <= A_t + B_t + |k/W-p|,
    A_t = sup_(x>=0) |Hhat_t(x)-Hbar_t(x)|,
    B_t = sup_(x>=0) |Hbar_t(x)-H_t(x)|.

If L=sup_(u>=0) u g(u) is finite, the derivative of G(exp(eta)x) with respect to eta is exp(eta)x g(exp(eta)x), so

    B_t <= (L/W) sum_(i=t-W)^(t-1) |eta_i-eta_t|.

This separates empirical fluctuation, relative-scale-error drift, and the quantile discretization term. It is NOT a distribution-free finite-sample coverage theorem, and A_t is not automatically an iid empirical-process error. The random H_i are conditional laws, not unconditional CDFs.

Possible additional bound, to be independently checked: assume |eta_i|<=B almost surely, g bounded by M_g, q_t in [0,Q], and deterministic W. Use the corresponding decomposition with A_t restricted to [0,Q]. On a fixed grid x_j=jQ/J, conditional Hoeffding plus a union bound over grid points gives, with probability at least 1-delta, grid error at most sqrt(log(2(J+1)/delta)/(2W)). Monotonicity and the e^B M_g-Lipschitz property of Hbar_t extend this to all x in [0,Q] with an extra e^B M_g Q/J term. The condition q_t<=Q must be explicit or controlled with an additional tail event. For many origins/window candidates, account for the extra union. For data-selected weights, do not reuse the martingale calculation without checking predictability. A plug-in "effective sample size" is not a substitute for a proof.

An estimated-mean extension is a later task. It adds location error through the two tails of Z; do not silently reuse the pure-scale formula. Shape drift likewise adds a separate discrepancy between innovation CDFs.

### 7.3 Exact finite-window contamination law after scale recovery

This controlled case isolates H2 without EWMA/GARCH estimation noise.

Assume the current mean and scale are exact. Of W historical independent scores, W-m have law U=|Z| and m have law cU, c>0. The membership of the m observations and c are DETERMINISTIC, not selected from realized outcomes. Let q be their kth order statistic and let U_0 be an independent new draw from G. Then

    Coverage(W,m,c,k)
      = integral_0^infinity P(A_u+B_u <= k-1) dG(u),
    A_u ~ Binomial(W-m, G(u)),
    B_u ~ Binomial(m, G(u/c)),

where A_u and B_u are independent for each fixed u.

Proof: conditional on U_0=u, U_0<=q is equivalent (almost surely, by continuity) to having at most k-1 historical scores below u. Counts in the two independent groups have the displayed binomial laws. Integrate over u.

For m=0 or c=1, the result is k/(W+1). Coupling the same independent U_i before and after multiplying m coordinates by c proves that c>1 stochastically increases q and coverage relative to this clean rank baseline; c<1 decreases them. This is a statement about repeated-sample coverage, not a claim that every realized conditional coverage exceeds p.

Interpretation: if a scale predictor underestimates sigma by a factor c for d origins and then becomes exact, those d vintage scores remain inflated. For fixed d<=W, after recovery their number is

    m_t = |[t-W,t-1] intersect [tau,tau+d-1]|.

It can take W further forecasts after recovery before the last contaminated score exits. Once it exits, the clean marginal rank law returns. Transient scale overestimation following a downward shock can leave a later undercoverage tail by the same mechanism.

This rank-mixture identity does NOT automatically apply to data-dependent EWMA errors: there the scale ratios are adaptive and correlated with earlier innovations. Use the identity as a reference experiment; use the decomposition or a new proof for realistic scales.

Checked Gaussian examples (W=250, k=239):
- clean window: 0.9521912351;
- m=25, c=3: 0.9895534019;
- m=25, c=1/3: 0.9469026586;
- m=50, c=3: 0.9991923377.

The numerical integral uses a Uniform(0,1) transform and converged Gauss-Legendre rules. An initial 256/512-node comparison missed a strict 2e-8 tolerance for the most extreme case; refinement to 512/1024 nodes reduced the disagreement below 1e-8. This was a numerical-integration resolution issue, not a change to the identity. Independent Monte Carlo agrees within the recorded Monte Carlo errors. Tests are evidence, not mathematical proof.

### 7.4 Boundary: an unannounced shock cannot be perfectly anticipated

Consider two processes with identical observed histories but different next-step Gaussian variances. An online algorithm produces the same finite interval for both histories. If the larger next-step scale is unrestricted, its next-step coverage can be made arbitrarily small. Thus the project must not promise immediate finite-width conditional validity against arbitrary unannounced variance jumps. Oracle methods receiving the new scale are privileged diagnostics, not deployable competitors.

## 8. Exploratory pilot already executed

Configuration: 200 independent paths; 2,600 observations; known zero mean; iid N(0,1) innovations; true standard deviation 1 until zero-based t=1200, 3 for t=1200,...,1799, then 1. Evaluation is t=1000,...,2599. Estimated scale uses causal EWMA with decay 0.94 and initial variance 1. Every method uses the same paths and only past outcomes, except explicitly labeled true-scale oracles.

Selected realized coverage results:

| Method | All evaluation times | First 25 after upward shift | Mean width / ideal oracle width, all evaluation times |
|---|---:|---:|---:|
| Raw rolling, W=250 | 0.942828 | 0.537200 | about 1.195 |
| EWMA-normalized rolling, W=250 | 0.952419 | 0.834200 | about 1.079 |
| Oracle-scale rolling, W=250 | about 0.9522 | 0.954000 | about 1.017 |
| Full Gaussian oracle | about 0.9496 | 0.949000 | 1.000 |

Use `reference/synthetic_baseline_v1/pilot_results/summary.csv`, not rounded table entries, as the numerical source of truth. It also contains analytic conditional coverage averaged over simulated histories, interval scores, and replicate-level Monte Carlo standard errors.

This confirms that acceptable full-run coverage can coexist with poor immediate post-shift performance in this PARTICULAR setting. It does not establish a novel phenomenon or show that any new algorithm beats strong comparators.

W=50 variants are also included, but their iid corrected-rank benchmark is 49/51=0.960784, whereas W=250 has 239/251=0.952191. Do not attribute their whole coverage difference to adaptivity. For the formal benchmark use W in {99,199,399,799}, which permits integer ranks at both 90% and 95%, or otherwise report the rank offset explicitly.

Passed implementation checks: future-suffix mutation leaves all forecasts through the mutation origin unchanged; multiplicative unit changes rescale intervals appropriately; full oracle radii match the analytic normal quantile.

## 9. Experimental program: staged, not one giant sweep

### Stage A: reference theory and falsification

Implement the deterministic transient-error experiment first. Vary d/W, multiplier c, W, and innovation distribution. Compare the exact rank-mixture integral with Monte Carlo. Include c>1, c<1, no error, constant multiplicative bias, and a scale shock with a perfect scale oracle. This is the cleanest test of the proposed mechanism.

### Stage B: realistic scale and memory interaction

Use Y_t = mu_t + s_t sqrt(h_t) Z_t with

    h_t = (1-rho) + (a Z_(t-1)^2 + b) h_(t-1),
    a=0.05, b=rho-a, rho in {0.70,0.90,0.98}.

For stable innovation variance 1, this parameterization fixes the stationary inner variance E h_t=1. The deterministic multiplier s_t separates an external scale change from endogenous GARCH persistence. Name it scale-modulated GARCH, not an unchanged ordinary GARCH model at the break. Discard a fixed burn-in (e.g. 5,000) before model fitting/evaluation; verify initialization sensitivity and moment conditions. Gaussian and standardized t_5 innovations form the initial two noise families.

Core scenarios:
- D0: constant scale, iid innovations, no shift.
- D1: deterministic upward/downward scale step, including a temporary pulse; multipliers 2 and 3 initially.
- D2: stationary GARCH at three persistence values, no structural break.
- D3: GARCH plus an external scale step or pulse.
- D4: gradual log-scale ramp.
- D5: innovation-shape change at fixed variance, e.g. normal to standardized t_5; later add skewness only if needed.
- D6: mean-model misspecification, treated as a separate robustness scenario, not hidden inside the pure-scale mechanism test.

Do not run the full Cartesian product immediately. Choose a small balanced development design, retain a manifest of all tried configurations, then lock a confirmation design with new seeds and at least one unseen shift profile. The current pilot and all its seeds are DEVELOPMENT evidence.

Causal scale estimators:
- Constant training-period scale (weak reference).
- EWMA with half-lives in {8,32,128}; decay=2^(-1/half_life).
- Fitted GARCH(1,1), with a documented past-only fitting window and periodic refit schedule; filtering uses only earlier observations.
- True scale and oracle-with-deterministic-lag, labeled diagnostic only.

For each scale, calibrate its own vintage residual sequence. Do not select the most accurate scale from the test segment.

### Stage C: minimal strong comparison set

Hold the point forecast and available information fixed for all intervals. Compare:
1. Model-based Gaussian or standardized Student-t intervals with causal scale forecasts.
2. Raw rolling absolute-error quantile intervals.
3. Normalized rolling absolute-error quantile intervals at several W values.
4. Normalized ACI: same scores as (3), adaptive alpha update from past realized coverage errors.
5. SPCI through a faithful implementation or an explicitly named shared-forecast adapter.
6. One strong adaptive comparator: SAOCP or PID in the first pass; include the other if its overlap matters for a final new-method claim.
7. True-scale rolling and full distribution oracle as diagnostic references only.

Do not quietly simplify SPCI's asymmetric interval or residual quantile mechanism into our symmetric score quantile. A symmetric ablation is a distinct variant. Read the author implementation, pin the commit/license, and test the adapter. Two tracks are acceptable: a shared-predictor wrapper comparison, and a separate faithful end-to-end replication; do not blend their conclusions.

For ACI, use alpha_(t+1)=alpha_t+gamma*(alpha-error_t) with the exact documented extended-quantile behavior. Infinite/empty sets can occur. Count and report them; do not cap widths, clip alpha silently, drop difficult dates, or report a finite-subset mean as if it were the unconditional mean. A clipped practical variant must have a different method name and no inherited theorem claim. Similar care applies to score bounds and saturation choices in SAOCP/PID.

### Stage D: at most one low-complexity candidate

Only if Stages A-C show a meaningful memory-lag failure beyond existing baselines, test an age-based, scale-triggered short-memory calibration rule as a HYPOTHESIS, not a claimed invention.

A simple test specification: with a shared causal scale sequence, define D_t=abs(log(sigmahat_t)-log(sigmahat_(t-l))) using l=5. If D_t exceeds a development-chosen threshold, use W_short=99; otherwise W_long=399. Retain short mode for a predeclared hold period (e.g. 20) after the last trigger. Threshold candidates and hold periods must be small, fixed before confirmation, and tuned using separate development data. These are provisional design values, not theoretically optimal constants.

Keep all scores in order; do NOT remove individual large scores, winsorize them to improve coverage, or use the true change point/eta_t in the deployable rule. Report false-trigger costs in D0, and compare against always-short, always-long, and existing adaptive methods. This proxy detects changes in an estimated scale, not true changes in scale-estimation error; the mismatch is a central reason it may fail.

If it does not improve the honest tradeoff, discard the new-method claim. A theoretically grounded mechanism study remains possible if its analysis is genuinely distinct and consequential.

## 10. Metrics and uncertainty accounting

Predeclare alpha=0.05 as the main target and alpha=0.10 as a robustness target. Report exact k, W and the iid rank reference for each method where applicable.

Primary diagnostics:
- Overall realized coverage, and upper/lower tail errors separately.
- Event-time coverage at offsets after an upward and a downward change, aggregated across independent replications.
- Mean interval width; also oracle-normalized width in SIMULATIONS only.
- Central interval score: IS_alpha(l,u;y)=(u-l)+(2/alpha)(l-y)1{y<l}+(2/alpha)(y-u)1{y>u}. A wider interval is not automatically better.
- Post-event undercoverage area and overcoverage/width inflation separately; do not allow positive and negative coverage errors to cancel into an apparently good score.
- Run lengths of misses as a descriptive secondary metric, with an oracle reference and uncertainty; do not treat overlapping windows as independent tests.
- Runtime, calibration memory, fit failures, infinite/empty sets, warning/fallback frequencies.

For a predictable conditional distribution known in simulations, evaluate c_t=F_t(u_t)-F_t(l_t) directly. This reduces test-outcome noise while retaining uncertainty over histories. On real data, there is no observed true c_t. State-stratified coverage is a diagnostic, not proof of full-history conditional coverage. Define states from lagged information or from simulation truth for oracle diagnostics; selecting "high volatility" by the same current outcome changes the question.

Suggested event windows: first 25, first 100, and a later recovery window of length 200; predeclare them, along with evaluation horizon. Count first-shock errors rather than excluding them. Separate immediate-shock performance from post-learning recovery. Recovery time, if used, must specify tolerance, sustained-window requirement, and right-censoring when recovery is not observed.

Use paired independent replication as the primary uncertainty unit: compute each metric per replication, then paired method differences and Monte Carlo SE/intervals across replications. Choose final replication count after a pilot precision calculation; 200 for screening and up to 1,000 after the design is locked are caps/defaults, not substitutes for precision analysis. Multiple scenario comparisons require a predeclared primary contrast and appropriate multiplicity handling for confirmatory claims. Avoid treating thousands of adjacent dates as thousands of independent experimental units.

For real-data corroboration, first recover IBM provenance. Later select at least one dated public non-financial series plus dated financial series under a recorded protocol. Freeze snapshots and licenses. Do not pick crisis dates only after looking at which algorithm fails. Real-data evaluation can use block-based uncertainty methods with their assumptions stated; bootstrap does not cure arbitrary nonstationarity.

## 11. Chronological protocol and leakage tests

At each origin t:
1. Fit/update the location/scale model using outcomes strictly before t.
2. Save muhat_t, sigmahat_t, model-fit cutoff, selected calibration window, and all tuning state.
3. Build the interval from eligible historical vintage scores only.
4. Save the interval BEFORE observing Y_t.
5. Reveal Y_t; compute score R_t and coverage error.
6. Update scale filters, calibration histories, and any ACI/controller state for t+1.

Training, tuning/development, calibration initialization, and confirmatory test segments/replications must be explicit. Online updating on already revealed test outcomes is permitted under the locked protocol; using future outcomes or retuning hyperparameters on test performance is not.

Required tests:
- Future-suffix mutation and current-outcome mutation cannot change already issued intervals.
- Historical model cutoffs precede their associated outcomes; vintage scores are immutable.
- Full-sample standardization, model selection, centering and volatility fitting are forbidden in test forecasts.
- Quantile ranks, ties, insufficient calibration data, infinity and empty-set conventions match the method specification.
- Constant scale-bias cancellation and unit equivariance hold where claimed.
- Gaussian oracle conditional coverage is exactly 1-alpha; oracle rolling has the finite-rank marginal reference, not exact pathwise conditional coverage.
- Every baseline is evaluated on the same eligible forecast origins; failures are visible rather than removed.
- Synthetic oracle information is structurally inaccessible to deployable methods.
- Numerical identity checks pass over a grid, including c<1 and edge ranks.

Log enough information to audit forecast cutoffs. Preserve full traces for preselected replications and event windows; retain per-replication metrics for all runs and all configurations/seeds. Do not produce an unnecessary many-gigabyte artifact pile.

## 12. Go / revise / no-new-method decision

GO as a research project requires a precise question, credible prior-art differentiation, independently checked mathematics, and reproducible evidence on more than one favorable synthetic configuration. The decision is NOT determined by achieving a chosen p-value or winning a selected plot.

A mechanism paper may be defensible without a new algorithm if it contributes a substantive analytical characterization, demonstrates its practical relevance against strong methods, and identifies consequences not already supplied by prior work. The elementary identities alone may only support a technical note or reproduction project.

A new-method claim additionally requires consistent improvements on a predeclared calibration/efficiency tradeoff, against appropriately tuned existing methods, with comparable information and costs. If only the oracle works or fixed short windows explain all gains, do not inflate the conclusion.

REVISE when scale error, shape drift, rank rounding, model fitting, or selection bias explains away the apparent result. NO-NEW-METHOD is a legitimate outcome; preserve a clean negative result and identify the next narrowly justified question.

Before a final research title or abstract is adopted, the main identity, experimental controls, and novelty boundary should be explained independently from the underlying evidence.
