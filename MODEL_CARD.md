# Model card — trust-gated Bayesian optimisation

*Following the model-card framework (Mitchell et al.). Describes the optimisation approach used across the full 13 rounds of the BBO capstone.*

## Overview

**Name:** Trust-gated Bayesian optimisation with a portfolio of scoring rules.
**Type:** Sequential black-box optimiser — a predictive model per function plus a per-function scoring rule that picks the next query.
**Version:** final (13 rounds complete; the README's progress table is the version history).

## Intended use

**Suitable for:** finding good inputs to expensive, opaque functions when each evaluation is costly and the budget is tiny — of the order of tens of queries, not thousands. Problems like experiment design, process tuning, or any setting where you pay per test.

**Should be avoided for:** problems with plentiful evaluations (simpler methods win), functions that change over time (nothing here handles drift), or any setting where a single bad query is dangerous rather than merely wasteful — this approach deliberately spends queries on probes that are expected to "fail" informatively.

## Details — how the strategy evolved across ten rounds

The core loop never changed: fit a model to each function's history, score candidates with a rule, submit the best candidate, learn from the result. Everything else evolved.

- **Weeks 1–2:** broad exploration with one rule, then a family of rules matched to each function's character (sparse, noisy, high-dimensional).
- **Week 3:** a noise-aware refinement rule added; first evidence that some peaks sit exactly on corners.
- **Week 4:** a small neural network added to make suggestions in unexplored regions — it failed badly (predicted 2.14 on a function whose true value there was −17.9).
- **Week 5:** the **trust check** — hide each known point, ask the model to predict it, and refuse to act on any model that predicts worse than guessing the average. This exposed that three of the eight functions had models that were actively misleading.
- **Week 6:** trend tracking on the trust check, so one lucky week doesn't earn trust and one bad week doesn't destroy it.
- **Week 7:** a partition process borrowed from a NeurIPS competition entry — classify the search space into good and bad territory, model only the good part. Its debut went 0-for-5, but it pointed at the right neighbourhoods.
- **Weeks 8–10:** the endgame formula — tiny refinements near proven winners, triangulation where a faint signal appeared, and reproduction tests to check that banked results are real. Weeks 8 and 9 produced five new bests between them, all from careful moves.

## Performance

Final results per function (seed best → final-round return):

| Function | Seed best | Final return | Note |
|---|---|---|---|
| f1 | ≈ 0 | **+0.048** | source located in week 11 after eleven silent rounds; the final-round step beat the banked value by 53% |
| f2 | 0.611 | 0.588 | best observed 0.682 (week 9); revealed as noisy in the final round |
| f3 | −0.035 | −0.033 | never beaten by search; revealed as (mildly) noisy |
| f4 | −4.03 | **0.540** | week 2 winner; reproduced exactly twice — deterministic, razor-thin peak |
| f5 | 1 089 | **8 662.405** | 8× the seed; reproduced exactly three times |
| f6 | −0.714 | **−0.154** | improved in three separate weeks; mildly noisy at the top |
| f7 | 1.365 | **1.857** | improved twice from the same pocket; deterministic |
| f8 | 9.599 | **9.950** | improved in eight separate weeks; deterministic |

**Metrics used:** best-so-far per function (the headline), gain per query (the efficiency view), and the weekly trust score per model (the honesty view). No single metric tells the story — function 3's flat line and function 5's 8× jump are both part of the same strategy.

## Assumptions and limitations

- **Repeatability turned out to be a 4-of-8 property.** Functions 4, 5, 7 and 8 reproduce exactly at identical inputs; functions 2, 3 and 6 return different values on repeat queries. Two reproduction tests on two functions were not sufficient evidence to generalise to all eight — the project's final and most instructive miscalibration.
- **Peaks are assumed sharp.** Refinement uses tiny steps; where the top is actually flat this wastes queries.
- **The models assume smooth, consistent surfaces.** At least two functions visibly violate this, which is why the trust check exists.
- **Single observations are treated as facts** — an unavoidable consequence of the one-query-per-week budget, and the deepest validity limit of the whole exercise.
- **Failure modes seen in practice:** confident predictions in unexplored territory (weeks 4, 6 and 7) all produced poor results.

## Ethical considerations

Nothing here touches personal data, but transparency still matters: the value of this work to anyone else depends entirely on their ability to check it. Every query, every returned value, every rule choice and its reasoning is in the repository — the weekly reflections record what I believed at the time, including the beliefs that turned out wrong.

That is also what makes the approach adaptable: someone applying it to a real problem can see not just what worked but why the failures happened, and avoid repeating them.
