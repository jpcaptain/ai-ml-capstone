# Week 03 reflection — BBO capstone

1. How has your query strategy changed from earlier rounds? 

The strategy has shifted from broad exploration to per-function specialisation. Round 1 ran UCB on 7 of 8 functions — almost pure mapping, little trust in the model. Round 2 split the explore camp into four rules, each matched to a function's character: pure variance for the sparse zero-mean field of f1, Thompson sampling for noisy f2, MES (Max-value Entropy Search) for the high-D f8 where UCB had snapped to a corner, and UCB elsewhere. f4 and f5 moved to Expected Improvement because the model had a confident view of where to push. Round 3, with five new bests confirmed in Round 2, sees four of the eight functions move to exploitation (EI / PI) and the others stay in explore mode.

I tune the kernel rather than the acquisition: Matérn 5/2 with per-axis lengthscales (ARD), a WhiteKernel for noise, and scikit-learn's marginal-likelihood optimiser restarted ten times per fit. The per-axis lengthscales and noise level are model-fitted, not hand-set. Leave-one-out predictions is a sense check — a tight cloud along the diagonal means the model generalises on what it's already seen. What I still hand-tune is the acquisition choice itself and the β / ξ parameters.

2. How do you balance exploration against exploitation?

The mix shifts week-by-week as the data confirms or denies model predictions. Round 1 was 7:1 explore-to-exploit, Round 2 was 6:2, Round 3 is 4:4 — the swing isn't arbitrary. Each function moves to exploit only when a previous round has confirmed a real gain there: f4 jumped −4.0 → 0.26 → 0.54 under EI, f5 went 1 089 → 1 617 → 8 662 (UCB W1, then EI W2), f8 went 9.60 → 9.89 once MES replaced UCB.

The trade-off: every explore query forgoes a chance to bank a confirmed improvement, but every premature exploit risks chasing a hallucinated peak. Last round f5's earlier corner prediction was 1 639 vs an actual 1 089 — clear over-extrapolation. Untested regions still get sampled when the model has high uncertainty there; "the model looks confident here" alone is never the criterion.

3. How would SVMs change your approach?

A soft-margin SVM classifier fits naturally on f1 (radiation source detection). Label the known points "near a source" (non-zero reading) vs "background" (≈ 0) and the classifier learns the source-region boundary directly. Today every reading is essentially zero, so there is nothing to train on yet — but the moment one non-zero hit lands the binary lens becomes useful. The slack parameter matters because the boundary at the edge of a source's radius is noisy.

A kernel SVM (RBF or Matérn) would help any function with non-linear high-performance regions — f4, with its many local optima, is the obvious candidate. The kernel projects inputs into a space where a curved positive region becomes more separable. Downside vs the GP: an SVM gives a class label, but no native uncertainty estimate, so it cannot drive an acquisition function alone. Most useful as a secondary signal — "the GP predicts 0.5 and the SVM puts this point in the high class" is a stronger signal than either alone. 

4. What limitations of your current model become apparent as data grows?

Three areas I'm watching:

Computational cost. Leave-one-out diagnostics retrain the GP n times per function — fine at the current sizes, but already slowing on f8 (42 samples in 8D). Within a few rounds that will need adjusting.
Overfitting. The model has one "smoothness" setting per input, learned from the data, with a wide allowed range. If the fitter picks a setting that is too low for one input, the model just memorises the known points and then claims to be very sure about every point in between — when really it is chasing noise. The leave-one-out check is what catches this: hide each known point in turn, ask the model to predict it, then see how close the guess comes. When those guesses drift away from the diagonal (predicted = actual), the model has overfit.
Irrelevant dimensions. ARD is meant to handle this: a feature with a large lengthscale is effectively ignored. On f8 I expect two or three of the inputs to turn out near-irrelevant. Making that explicit is what SAASBO (sparse-axis-aligned priors) does, and it is the next experiment if MES stalls.
5. How does this black-box set-up prepare you to think like a data scientist?

Three habits this project has cemented:

Decide under uncertainty without waiting for proof. Every weekly submission goes in before the model is "ready" — there is no held-out test set, just a budget and a portal.
Treat predictions as evidence, not truth. f5's W1 prediction was off by a factor of five; the right move was to submit anyway, label it a probe, and update on the data.
Use the simplest lens that fits the sub-problem. Logistic regression for f1's binary source-detection, per-feature slice plots as a partial-dependence view — not the main tool but cheap secondary checks. Most ML projects benefit more from the right lens than the best model.
The general pattern is limited budget, opaque environment, conflicting signals, iterate-observe-adjust. Every real ML team faces some version of the same challenge. The discipline this capstone enforces — naming what the model is sure of, what it is guessing at, and what it has never seen.

