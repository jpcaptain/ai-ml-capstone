# The JetBrains partition approach — reflection

> Discussion-board activity. Keep under 700 words.

## 1. Core principles, key ideas and how it differs from traditional approaches

The JetBrains team (3rd place, NeurIPS 2020 Black-Box Optimisation Challenge) built their approach on one central idea: **don't try to model the whole search space with one model — learn which part of the space is good, and concentrate there.**

Their recipe has three steps. First, take every point you've tried and split them into two groups by score — a "good" group and a "bad" group. Second, train a classifier (they used an SVM) to learn *where* in the search space the good group lives — effectively drawing a boundary around the promising territory. Third, repeat the split inside the good region, up to five levels deep, like zooming in on a map. Then run a local optimiser only inside the final zoomed-in region, using only the points that live there.

Two supporting ideas: spread the early queries evenly so every dimension gets covered before you start zooming, and if you go several rounds without improvement, throw everything away and restart — a built-in escape hatch from local peaks.

Traditional Bayesian optimisation fits one model to the entire search space and asks "where should I try next?" — anywhere in the box. That works when the function behaves consistently everywhere. It struggles when the surface is smooth in one place and spiky in another, because a single model has to average out those differences.

The partition approach flips this. The classifier carves the box into territories first, and the model only has to describe the good territory — a much easier job. I saw this directly in my own project: my global model repeatedly over-predicted on function 4 (it once claimed 0.98 where the true value was 0.14) because it was averaging behaviour across regions that have nothing in common.

## 2. Advantages

**Efficiency** — designed for tiny budgets (the competition allowed 128 evaluations; my capstone allows fewer). Zooming concentrates queries where they count. **Accuracy** — a model fitted only on the good region isn't distorted by irrelevant far-away points. **Adaptability** — the partition is rebuilt as data accumulates. **Scalability** — the classifier handles the geometry, so the expensive model never sees the whole high-dimensional box.

Running my version on my eight functions, the two most sensible suggestions of the week came from it: on function 7 it proposed a point right beside my best-ever result (rather than wandering off like my other rules had done for four weeks), and on function 8 it independently landed on the same "input 5 should be high" signal two other methods had hinted at.

## 3. Limitations and drawbacks

The clearest one: **the local model can still be over-confident inside its own region.** On my function 4, the partition model predicted 2.77 — five times higher than anything ever observed there. Confining the search doesn't automatically make predictions correct.

Others: with very few points, the score-based split is unstable — clusters that form early may be noise. If the good region is oddly shaped, the classifier's boundary may cut off the true peak. The reset-and-restart mechanic costs precious budget on a tight allowance. And it inherits sensitivity to its own settings (split depth, classifier flexibility) — the team tuned those with a second optimiser.

## 4. Real-world applications

Anywhere evaluations are expensive and budgets are small: tuning machine-learning models where each training run takes hours; chemistry and materials experiments where each sample costs real money; engineering simulations (crash tests, aerodynamics); A/B tests where each variant needs a week of traffic. It shines where the response surface behaves differently in different places — which, in my experience with eight black-box functions, is most of the time.

## 5. Questions and recommendations for peers

Three tips from actually implementing it. **First, keep a sanity check on the local model's predictions** — if it forecasts values far beyond anything observed, treat the suggestion as a probe, not a fact. **Second, don't partition too early**: below roughly 15–20 points the split is guessing; start global, zoom later. **Third, run it alongside your existing approach, not instead of it** — comparing the two suggestion sets side by side told me more about my functions than either method alone. Where they agree, trust rises; where they disagree, that disagreement is usually the most interesting question of the week.
