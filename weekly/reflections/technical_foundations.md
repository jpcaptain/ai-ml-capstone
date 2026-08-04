# Technical foundations — reflection

> Required capstone component 17.2. Keep under 700 words.

1. Main technical justification

My approach is Bayesian Optimisation with a Gaussian Process surrogate — the dominant paradigm for sample-efficient optimisation of expensive black-box functions. The justification is well established: GPs give you both a predicted value and a calibrated uncertainty everywhere in the search space, and every standard acquisition rule (UCB, EI, PI, MES) is built on combining those two outputs. With 14–45 known points per function, GPs outperform neural-network surrogates on sample efficiency, and offer uncertainty quantification.

2. The single most influential paper

The most influential paper on my approach is Jones, Schonlau and Welch (1998), "Efficient Global Optimization of Expensive Black-Box Functions". It laid out the recipe I follow every week.

Their key idea is simple. When you can only afford a few queries, don't pick the point where the model predicts the highest score — pick the point where the expected improvement over your current best is highest. That balances chasing promising regions against probing uncertain ones.

This shapes my project in three ways. Expected Improvement is the scoring rule I use whenever a function's model is reliable enough to trust. The emphasis on uncertainty as a first-class signal is why I use Gaussian Processes — they give uncertainty for free. And their argument that not every query needs to chase the highest prediction is what justifies the informational probes I now deploy when the model is uncertain.

3. Third-party libraries

The library doing most of the work is scikit-learn. It bundles everything I need: a Gaussian Process tool that tunes itself, a neural-network tool for cross-checks, and a random-forest tool that gives me a third opinion on which inputs matter. I chose it over bigger deep-learning libraries like PyTorch or TensorFlow because my datasets are small — 14 to 45 known points per function. Those libraries are designed for thousands or millions of examples and a graphics card to run on, so they would offer no real advantage at this scale.

scipy gives me two routines I use every week: one that spreads candidate query points evenly across the search box, and one that fine-tunes the most promising candidates by climbing to their nearest peak.

numpy and pandas handle the data, matplotlib the diagnostic plots, and jupyter the weekly audit trail.

4. Documentation for GitHub

The README already includes the technical approach and a round-by-round progress table.
To make the academic grounding clearer, I'll add three things.

A References section at the end of the README listing each paper that informed the work, with a one-line note on how each idea shows up in the code.

A methodology document explaining the design decisions in narrative form: kernel choice, candidate generation, and the trust check that gates the rest.

A changelog mapping each weekly addition (noise-aware rule, neural-network surrogate, trust gate, trend tracking) to the paper or peer insight that motivated it.

5. Additional sources

Three additional sources I've come across, but have not yet explored.

Eriksson et al. (2019), "TuRBO" (Trust-Region Bayesian Optimisation): function 8 has 8 dimensions and 45 known points — already in the regime where standard BO struggles because the search space is too big to cover. TuRBO maintains a "trust region" around the current best — a smaller box where the algorithm believes its model — and shrinks it when predictions stop being accurate. If MES stops improving function 8, switching to TuRBO could be an option.

Eriksson & Jankowiak (2021), "SAASBO": assumes that in high-dimensional problems most inputs don't actually matter — only a few do. The algorithm automatically discovers which inputs are influential and ignores the rest. I'm doing this manually for function 8 by running three feature-importance methods and looking for consensus; SAASBO would do it rigorously and automatically as part of the optimisation loop.

If I'm really brave and have time, Garnett (2023), Bayesian Optimization textbook. This should be useful as a reference for any design decision I have to make — kernel choice, scoring rule, noise handling, balancing exploration and exploitation.