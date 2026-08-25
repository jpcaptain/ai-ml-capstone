# BBO Capstone — Bayesian Optimisation of 8 Black-Box Functions

> **Stage 2 of the Black-Box-Bayesian-Optimisation capstone.** Maximise eight unknown functions over the unit cube using as few queries as possible. One submission per function per week via the course portal; surrogate models and acquisition strategy iterate from one round to the next.

---

## At a glance

- **Goal** — find inputs that score as high as possible on each of 8 mystery functions.
- **Inputs** — each function takes `d` numbers in `[0, 1]` (`d` ranges from 2 to 8).
- **Outputs** — each query returns a single continuous score; I never see the formula.
- **Budget** — one query per function per week. Number of queries spent is the implicit cost.
- **Toolkit** — Gaussian-Process surrogate per function + a per-function acquisition function picking the next query.

## The eight functions

| Func | d | Application (per portal brief) | Surface character |
|------|---|----|----|
| f1 | 2 | Radiation / contamination source detection | Sparse — mostly ~0 except near sources |
| f2 | 2 | Mystery ML log-likelihood score | Noisy + multimodal |
| f3 | 3 | Drug discovery — 3-compound combination | Maximising a negated cost |
| f4 | 4 | Warehouse product-placement surrogate | Many local optima |
| f5 | 4 | Chemical-process yield | Typically unimodal, single peak |
| f6 | 5 | Cake recipe — 5 ingredients | Maximising negative of total penalty |
| f7 | 6 | ML hyperparameter tuning | Black-box; literature priors inform search |
| f8 | 8 | 8-param ML hyperparameter tuning | High-dimensional; global optimum hard |

---

## Technical approach

Same loop for every function, every round:

1. **Read** the input/output pairs gathered so far (10–40 starter points, +1 per round since).
2. **Fit** a Gaussian Process surrogate:
   - **Matérn 5/2** kernel with **per-axis lengthscales** (ARD) — each input gets its own bumpiness setting.
   - **WhiteKernel** for noise — lets `f2`'s noisy log-likelihood fit without forcing zero residual.
   - **`normalize_y=True`** so the output scale (f5 reaches ~8 600) doesn't distort kernel hyperparameters.
3. **Score** candidate inputs with an acquisition function — a scoring rule that weighs "model thinks it's high here" against "model has no idea here".
4. **Optimise** the acquisition over the unit cube:
   - Scatter `2^12`–`2^14` Sobol candidates (depending on `d`).
   - Take the top 10 by acquisition score.
   - Polish each with **L-BFGS-B** (box-constrained quasi-Newton) to find the local peak.
   - Keep the best.
5. **Submit** the winner's coordinates to the portal in the required 6-decimal hyphen-joined format.
6. After the portal returns the score, **append** it to the function's CSV — the model sees it next round.

### Acquisition functions implemented

| Mode | Rule | Behaviour | Used for |
|------|------|-----------|----------|
| **Explore** | UCB (mean + β·std) | Chases uncertainty *and* high-mean spots | General mapping (default `β = 3`) |
| **Explore** | Variance (std²) | Pure max-entropy probing | Sparse zero-mean landscapes (f1) |
| **Explore** | Thompson sampling | Joint posterior draw, take its argmax | Noisy posteriors (f2) |
| **Explore** | MES (Max-value Entropy Search) | Score = expected info gain about the maximum's *value* | High-D where UCB snaps to corners (f8) |
| **Balanced** | EI (Expected Improvement) | Expected size of beating the current best | Once the model has a sense of where the peak is |
| **Balanced** | AEI (Augmented EI) | EI × `(1 - σₙ/√(σ² + σₙ²))` — discounts noisy candidates | Noisy functions where plain EI chases the noise floor (f2) |
| **Optimise** | PI (Probability of Improvement) | Chance of beating the current best | Late stage — squeeze around the incumbent |
| **Lock-in defence** | `far` (predicted-value × distance-to-data, GP-driven) | Favours high-predicted unmapped regions over local-peak shoulders | When the worry is "stuck on a local high" |
| **Lock-in defence** | `nn_far` (same, NN-driven) | NN extrapolates trends into empty regions where the GP reverts to prior | When the GP under-values the unmapped space |
| **Model-free** | `space_fill` (pure max-distance to known points) | Ignores the GP entirely — spreads queries evenly across the unit cube | When LOO R² is negative (the surrogate is fitting noise and any GP-driven score is arbitrary) |
| **Partition** | `partition_bo.py` (KMeans-on-scores → RBF-SVM region boundary → local GP + EI inside the region) | Learns which part of the box is "good", fits a local model there, confines candidates to it | Non-stationary surfaces where one global lengthscale fails; after Sazanovich et al. (NeurIPS 2020 BBO Challenge, 3rd place) |

Choice per function shifts week-to-week as data accumulates. Early rounds bias **explore**; later rounds shift toward **EI → PI** as the picture firms up.

---

## Repository layout

```
.
├── bo.py                         # The whole toolkit (GP, acquisitions, plots, driver)
├── partition_bo.py               # Search-space-partition process (JetBrains NeurIPS 2020 recipe)
├── DATASHEET.md                  # Datasheet for the query-history data set
├── MODEL_CARD.md                 # Model card for the optimisation approach
├── data/                         # Working CSVs — one per function, grows +1 row per round
│   ├── f1.csv … f8.csv
│   ├── function_descriptions.csv
│   └── r2_history.csv            # Weekly trust-score record per function
├── initial_data/                 # Read-only seed inputs/outputs (.npy) from the portal
├── outputs/
│   └── weekNN/                   # Posterior + acquisition plots, raw portal returns per round
├── weekly/
│   ├── weekNN.ipynb              # Round driver — fits, proposes, plots, generates submission strings
│   └── reflections/
│       └── weekNN.md             # Written reflection per round (700-900word cap, course requirement)
└── README.md
```

**Documentation:** the [Datasheet](DATASHEET.md) describes the query-history data set (what it contains, how it was collected, its gaps and appropriate uses); the [Model Card](MODEL_CARD.md) describes the optimisation approach (strategy evolution across the ten rounds, performance per function, assumptions and failure modes).

## Quickstart

```bash
pip install numpy pandas scikit-learn scipy matplotlib jupyter
jupyter notebook weekly/weekNN.ipynb
```

Run the cells top to bottom. The notebook:
1. Seeds the working CSVs from `initial_data/` (no-op on subsequent runs).
2. Fits all 8 GPs and proposes the next query per function.
3. Renders the diagnostic plots (2D heatmaps for f1/f2; 1D slices through the incumbent for higher-D; convergence + leave-one-out for every function).
4. Prints the 8 submission strings to paste into the portal.
5. Drops a starter reflection at `weekly/reflections/weekNN.md`.

When the portal returns the scores, paste them into the final cell to append the new row per function.

**A note on notebook outputs:** every weekly notebook is a period-correct record. Weeks 1–2 retain their original executed outputs; weeks 3–11 were re-executed against their exact point-in-time data (the CSVs preserve submission order, so each week's data state is reconstructible by truncation), and all 72 regenerated submissions were verified to match the CSV record byte for byte; week 12 was executed against the full current data. The per-round PNG files in `outputs/weekNN/` show the same period-correct views.

---

## Progress (live)

| Round | Acquisition mix | New bests | Headline |
|---|---|---|---|
| W1 | 7 × UCB(β=3), 1 × EI (f4) | **2** — f4, f5 | f5 corner gamble: 1 089 → 1 617 |
| W2 | 3 × UCB, 4 × diversified Explore (variance, Thompson, MES), 2 × EI | **5** — f4, f5, f6, f7, f8 | f5 all-1s corner 1 617 → **8 662** (5.4×); MES delivered on f8 (9.60 → 9.89) |
| W3 | 3 × UCB, var (f1), AEI (f2), 2 × PI (f4, f5), MES (f8) | **1** — f8 (+0.06) | First exploit-leaning round (4:4). f5 **confirmed deterministic** at (1,1,1,1) = 8 662.405. PI on f4 tightened to a worse spot (0.54 → 0.44). UCB on f6, f7 lost ground — surfaces are steeper than the GP thinks. |
| W4 | far (f1), AEI-xi=0.05 (f2), UCB (f3), 3 × **nn_far** (f4, f6, f7), var (f5), MES (f8) | **0** | **NN hallucinated badly.** f4 NN predicted 2.14, actual −17.92 (catastrophic miss). f7 NN predicted 1.88, actual 0.44. f5 var probe at non-corner returned 61.8 (confirms peak is uniquely at (1,1,1,1)). f8 MES essentially converged (9.95 → 9.9498). **Lesson: don't trust NN extrapolation at 13-43 sample sizes.** |
| W5 | 3 × **space_fill** (f1, f3, f7), 2 × AEI-xi=0.10 (f2, f6), EI (f4), PI near-corner (f5), MES (f8) | **0** | **LOO R² trust gate added.** Zero new bests on portal, but four functions' surrogate trust *improved*: **f3 promoted BROKEN → RELIABLE** (R² −0.23 → +0.67); f5 trust jumped (+0.76 → +0.94) and the near-corner probe proved the peak is **sharp** at (1,1,1,1) — no plateau. f6 demoted PARTIAL → BROKEN. f4 EI also missed. RF feature importance on f8 flagged x5 as more important than smooth-kernel methods can detect — pencilled for future probe. |
| W6 | 3 × `space_fill` (f1, f6, f7), 2 × AEI-xi=0.10 (f2, f3), EI (f4), **manual (0,0,0,0) probe** (f5), MES (f8) | **0** | **Trend-aware gate added.** f5 opposite-corner test returned 163 (vs peak 8 662) — **NO hidden second peak; (1,1,1,1) confirmed global**, safe for final-week lock. **f4 EI hallucinated again** (predicted 0.98 ± 0.22, actual 0.14 — 3.8 sigma off) despite R² = +0.98 — the trust gate catches LOO calibration but not extrapolation over-confidence. f6 recovered BROKEN → PARTIAL after the space_fill probe. |
| W7 | **Partition-BO debut** (f2, f4, f6, f7, f8), EI promotion (f3), space_fill (f1, f5) | **0** | Partition went **0-for-5** on debut — over-confident everywhere except f7 (returned 1.03, best f7 result in 5 weeks, still below the 1.688 incumbent). **f4's gamble failed a third time** (pred 2.77, actual −4.73 — its good region is razor thin). **The high-x5 hunch on f8 was disproven** (pred 10.13, actual 9.03). f5's quadrant probe returned 154 — another region ruled out. The round's real prize: **f1 returned its first non-zero reading in 7 weeks** (−0.0053 at (0.41, 0.47)) — there is structure near the centre. |
| W8 | **LLM-reasoned** (f1), **tight-refine** (f4, f7), AEI (f2, f6), EI (f3), space_fill (f5), MES (f8) | **3** — f6, f7, f8 | **Best round since W2, and all three wins came from conservative moves.** f7 tight-refine predicted 1.698, returned **1.839** (+0.15). f6 AEI jumped −0.705 → **−0.254** (+0.45). f8 MES nudged the converged point to a marginal new best. f4's ±0.02 perturbation returned 0.513 — the 0.540 peak is narrow. f1's probe toward centre came back ~4 000× weaker than the W7 reading — the structure sits the *other* way from centre. |
| W9 | llm_probe (f1), AEI (f2), EI (f3), micro-refine ±0.01 (f4), space_fill (f5), **tight-refine on the new winners** (f6, f7), MES (f8) | **2** — f2, f8 | **f2's first improvement in nine weeks**: 0.611 → **0.682** from a conservative near-incumbent probe. f8's third consecutive marginal MES nudge (9.94993). **f4 alarm**: the ±0.01 refine cost 0.23 — *worse* than W8's ±0.02 — distance doesn't predict loss, so f4 is likely noisy or razor-rugged; exact-coordinate reproduction test moved up to W10. f1 bracketed the hot spot: (0.41, 0.47) still strongest, next probe goes perpendicular. f6 near-reproduced (−0.264) — its basin is locally flat, good for the lock. |
| W10 | llm_probe perpendicular (f1), tight-refine (f2, f6, f7), AEI (f3), **exact repro test** (f4), space_fill (f5), MES (f8) | **1** — f8 | **f4 REPRODUCTION TEST PASSED**: 0.5401292083386946 vs W2's 0.5401292083386875 — identical to 12 decimals. Combined with f5's W3 reproduction, the portal functions are **deterministic**: every banked best is safely lockable, and W9's ±0.01 loss was ruggedness, not noise. f8's 4th consecutive marginal MES nudge. f1's perpendicular probe found nothing — the hot spot is tight around (0.41, 0.47). f6 (−0.263) and f7 (1.819) both landed close to their winners; winners stand. |
| W11 | llm_probe hot-box (f1), tight-refine ±0.01 (f2, f3, f6, f7), micro ±0.005 (f4), space_fill (f5), MES (f8) | **4** — f1, f6, f7, f8 | **Best round of the project.** f1's hot-box probe returned **+0.0027 — the first positive reading ever** (sign flips from −0.0053 within ~0.015: the structure is sharp and we're on top of it). f6 −0.254 → **−0.150** (+0.105). f7 1.839 → **1.857**. f8's 5th consecutive MES nudge. f4's ±0.005 cost 0.05 — the razor peak's exact coords are the lock. f5's free probe found 3 552 near (1, 0.97, 0.96, 0.28) — biggest non-corner value seen. |
| W12 | signal_step (f1), tight-refine (f2), partition (f3), axis probe (f4), space_fill (f5), **PCA-aimed steps** (f6, f7), MES (f8) | **2** — f1, f8 | **f1's reading grew 11.7× to 0.0315** — the line through the sign flip keeps climbing and hasn't turned over. f8's 6th consecutive MES improvement crossed 9.95. PCA-aimed steps on f6/f7 both landed below their winners — the pockets' peaks appear to be the winners themselves. f4's single-axis +0.005 probe cost 0.10: exact-coordinates lock only. New **PCA-aimed stepping**: the top-6 points of each live pocket are projected onto their principal axis and the tiny step follows the uphill direction — on f7 the top-6 scores order perfectly along that axis. f1 continues the line through the sign flip to (0.43, 0.455). Free slots (f3, f4, f5) take no-risk probes; locks are guaranteed by the reproducibility results. |
| **Final** | best-ever locks (f2–f8), **signal push** (f1) | — | **The push paid: f1 returned 0.0481, beating the banked 0.0315 by 53%.** The locks revealed a final finding: f4/f5/f7/f8 reproduced exactly (deterministic), while **f2, f3 and f6 returned different values at identical coordinates — genuinely noisy functions**. Determinism was a 4-of-8 property; two reproduction tests on two functions were not sufficient to generalise to all eight. |

Current best scores per function:

| Func | Best so far | At input | Acquisition that found it |
|---|---|---|---|
| f1 | **+0.0481** | (0.44, 0.45) | final-round signal push — the deliberate gamble, +53% over the banked value |
| f2 | **0.682** | (0.70, 0.05) | AEI (W9) — first improvement over the seed |
| f3 | −0.035 | seed point | not improved since seed |
| f4 | **0.540** | (0.41, 0.42, 0.35, 0.44) | EI (W2); **reproduced exactly in W10** — deterministic, razor-thin peak |
| f5 | **8 662.405** | (1, 1, 1, 1) | EI (W2); **confirmed deterministic** in W3, **peak proven sharp** in W5 (x4→0.92 dropped score by 1 314) |
| f6 | **−0.150** | (0.46, 0.38, 0.60, 0.73, 0) | tight-refine (W11) |
| f7 | **1.857** | (0, 0.13, 0.05, 0.17, 0.33, 0.64) | tight-refine (W11) |
| f8 | **9.95001** | (0.12, 0.15, 0.12, 0.21, 1, 0.55, 0.26, 1) | MES (W12 — sixth consecutive marginal nudge) |

---

## How this consolidates the course material

| Concept | Where it shows up here |
|---|---|
| **Linear regression** | Used as a conceptual *lens*, not the surrogate. The 1D-slice diagnostics (`plot_slices`) are essentially the linear-regression "hold others fixed, vary one feature" view — a per-feature accountability check before each submission. |
| **Logistic regression** | A natural fit for sub-problems with a clear threshold. **f1** ("near a source vs background") is the obvious candidate — once a non-zero reading lands, a logistic classifier could learn the source-region boundary. **f5** ("yield > threshold") is another. Not yet deployed; pencilled in. |
| **Gaussian Process regression** | The chosen surrogate. Gives mean + uncertainty everywhere, which is what every acquisition rule consumes. The kernel is the modelling lever. |
| **SVMs** *(to fold in)* | Same kernel-trick lineage as GPs — Matérn / RBF kernels carry across. Will compare an SVR surrogate on a noisy function (f2) once the course module lands. |
| **Iterative modelling** | The heart of this project. Each week's submission strategy is rebuilt on top of the prior round's portal returns — not just appending data, but switching acquisition rules based on what worked (e.g. UCB → MES on f8 after the W1 corner-snap). |

---

## Roadmap

- **Week 3 (next round)** — tighten the recent winners. f4 / f5 / f7 / f8 candidates for **EI → PI**; f1 / f2 / f3 remain in explore mode.
- **TuRBO trust regions** — if MES stalls on f8, restrict the search to a shrinking local box around the incumbent (standard high-D BO answer).
- **SAASBO** — sparse-axis priors to identify which of f8's 8 inputs actually matter.
- **Logistic classifier for f1** — once a non-zero reading lands, fit a "source vs background" classifier as a secondary signal alongside the GP regression.
- **SVR comparison on f2** — kernel methods on the noisy multimodal surface, once the SVM module is covered.

## References

- Brochu, Cora, de Freitas (2010). *A Tutorial on Bayesian Optimization of Expensive Cost Functions.*
- Wang, Jegelka (2017). *Max-value Entropy Search for Efficient Bayesian Optimization.* ICML.
- Eriksson, Pearce, Gardner, Turner, Poloczek (2019). *Scalable Global Optimization via Local Bayesian Optimization* (TuRBO). NeurIPS.
- Rasmussen & Williams (2006). *Gaussian Processes for Machine Learning.* MIT Press.
- scikit-learn — `GaussianProcessRegressor` and kernel docs.

---

*Stage 2 of the BBO capstone — work in progress, updated each round.*
