# Week 02 reflection — BBO capstone

How I approached this

Same recipe as last week: fit a Gaussian Process to each function's known points, score candidate inputs with an acquisition function, query the highest. New this round: I broadened **Explore** because UCB alone fails on sparse / noisy / high-D structures, and the new variants each target one of those.

- Explore — UCB (β = 3) chase uncertainty; Variance pure max-entropy probing for sparse landscapes; Thompson for noisy posteriors; MES for high-D where jumping to corners is misleading.
- Balanced — EI: trade off "might be high" against "unsure".
- Optimise — PI: squeeze around the current best.

Continue the strategy of exploration in the early rounds (now with four functions); later rounds shift toward Optimise as the picture firms up.

1. Main change in strategy
_What was the main change this week vs last? What prompted it — model predictions, acquisition function behaviour, or something else?_

Last week 7/8 functions ran UCB. This week 3/8 stay on UCB — split the Explore camp into four rules to match different scenarios:

- f1 → variance (sparse zero-mean field; uncertainty has to drive the probe).
- f2 → Thompson (noisy posterior; joint sample handles noise).
- f8 → MES (high-D, where UCB snaps to corners).
- f4, f5 → EI (both hit new bests last week: −4.03 → 0.26 and 1089 → 1617).

What prompted it: acquisition behaviour, mostly. f8's UCB pick last week was 7 zeros + 1 one — the GP extrapolating into empty corners, is not helpful. f4 / f5 by contrast scored real gains under their picks, so leaning further into exploitation made sense.

2. Exploration vs exploitation
_Did you focus more on exploration or exploitation? Why? What trade-offs did you weigh?_

Still learning toward explore — 6/8 on an 'Explore' rule, only f4 and f5 exploiting. With 10-40 points in 2-8D, most surfaces aren't mapped enough to commit to anything.

Trade-off: every explore query costs a chance to bank a confirmed improvement. But committing early to a corner-extrapolated "max" (the f5 / f8 risk last week) potentially wastes a query. Exploring with the right rule — variance for sparse, Thompson for noisy, MES for high-D — hopefully is cheaper in terms of number of goes than EI. I will deploy EI once the model has learned where the action is.

3. Outside influences
_Have any participant strategies, class discussions or recent outputs influenced this week's submission?_

Class introduced logistic regression this week. It didn't change my acquisitions — but I did wonder if I could deploy it as a classification between "near a source vs background". I came to the conclusion I need to continue exploring as I don't yet know where the sources are.

A Bigger influence: last week's portal returns. f4 +4.3, f5 +528, f8 essentially flat. The numbers told me that exploration is still the right strategy for 6/8 until we lock onto data points that show some promise.

4. Where a linear / logistic fit would break
_Which assumptions would a simple linear/logistic fit on one function violate? Response shape, noise, features?_

Take f2 (noisy, 2D, 11 points). Linear regression breaks in at least three places:

- Linearity — most likely multimodal with many local peaks.
- Constant-variance noise — noise level unknown and probably uneven.
- Features vs samples — 11 points; any polynomial basis rich enough to fit the bumps over-fits immediately.

5. Linear regions / decision boundaries
_Any roughly linear regions or possible decision boundaries? How might a logistic classifier perform in a threshold scenario?_

**f1** (radiation, sparse) has clean binary structure: "near a source" vs "background". A logistic classifier using 'reading ≠ 0' might draw a usable boundary around each source. This could be something to try next week.

6. Interpretability / per-feature effects
_Did considering individual feature effects help before deciding the query point?_

Yes, indirectly. I'm using 1D slice plots to "hold other features fixed, while varying one feature"

Concrete use this week: f5's slices showed the model climbing along x3 and x4 toward the upper edges → motivated the all-1s corner submission. f8's slices showed steep cliffs in several dimensions at once.