Section 1: Project overview

The BBO (Black-Box Bayesian Optimisation) capstone gives you eight mystery functions and asks you to find the inputs that score as high as possible — using as few queries as you can. I never see the formulas; I only see the score the portal returns for inputs I submit. One submission per function per week.

Why this matters: most real ML problems look like this. Hyperparameter tuning, A/B allocation, drug screening, manufacturing process optimisation — all are expensive-to-evaluate black boxes under a budget. The course brief is explicit about the applications: f1 is radiation source detection, f5 is chemical-process yield, f7 / f8 are ML hyperparameter tuning. Same technique, real problems.

Career angle: When building data heavy products, often there are trade-offs to be made, A/B testing, churn prediction, engagement prediction, all scenarios with a level of uncertainty, that need to be optimised.

Section 2: Inputs and outputs

Per function:

Input — d numbers in [0, 1], where d runs from 2 to 8 depending on the function.
Format — six-decimal values joined with hyphens. Example for a 2D function: 0.496189-0.999917. 
Output — a single continuous score from the portal. No gradient, no error bars, just one number.
Cost — one query per function per week. The budget is implicit: total queries spent.
Section 3: Challenge objectives

Maximise every function. The portal frames some as negated costs (f3 = −adverse reactions, f6 = −recipe penalty) but those are pre-negated so maximisation is the universal rule.

Constraints I have to work around:

Query budget — one per function per round. Three rounds in; each function now has 12 to 42 known points.
Response delay — results come back after the week's submission window. No real-time loop.
Unknown structure — no formula, no derivative, no monotonicity guarantee. f2 is noisy; f8 is high-dimensional; f1 is sparse (most readings ≈ 0). Each function has its own failure mode.
Boundary effects — inputs are confined to the unit cube; the global maximum can sit on a corner (f5 = (1,1,1,1) confirmed it does).
Section 4: Technical approach

For each function, every round: fit a Gaussian Process surrogate to the known points, score candidate inputs with an acquisition function, submit the highest scorer.

The GP uses a Matérn 5/2 kernel with per-axis lengthscales (ARD — each input gets its own bumpiness setting) plus a WhiteKernel for noise. scikit-learn fits the hyperparameters by restarting the marginal-likelihood optimiser ten times per round — not hand-set.

Six acquisition functions, picked per function per round:

Explore — UCB (general mapping), Variance (sparse landscapes), Thompson sampling (noisy posteriors), MES (high-D where UCB snaps to corners).
Balanced — EI (Expected Improvement).
Optimise — PI (Probability of Improvement).
What makes the approach mine: each function has its own way of breaking a generic rule, and I pick the acquisition that handles that specific problem rather than running the same rule on all eight. f8 in 8D needs MES because UCB's uncertainty estimate blows up at the corners and proposes nonsense; f1 sparse-zero-mean needs pure variance because EI / UCB are useless until something non-zero lands; f2 noisy needs Thompson because joint posterior draws respect the noise in a way rules that score one point at a time do not.

Exploration vs exploitation shifts as the data confirms or denies predictions. R1 was 7:1 explore-to-exploit, R2 was 6:2, R3 is 4:4. A function only moves to exploit once a prior round has confirmed a real gain there: f4 went −4.0 → 0.26 → 0.54 under EI, f5 went 1 089 → 1 617 → 8 662, f8 went 9.60 → 9.89 once MES replaced UCB.

Where the broader course material fits: linear regression as a per-feature lens (the 1D slice plots = partial-dependence view); logistic regression as a binary sub-problem solver (f1 "near source vs background" once a non-zero reading lands); SVR as a kernel-method comparison surrogate for noisy f2