# Repository, libraries, documentation — reflection

> Final activity of this module. Keep under 700 words.

Repository structure

Capstone/
├── README.md - Living doc, updated every round
├── bo.py - The whole toolkit in one file
├── data/ - Working CSVs, one per function — gain a row each round
├── initial_data/ - Read-only starter data from the portal
├── outputs/
│ └── weekNN/ - Plots and raw portal returns for each round
└── weekly/
├── weekNN.ipynb - Round driver notebook
└── reflections/
└── weekNN.md - Weekly written reflection

The flow is one notebook per round and one CSV per function that grows by a single row each time the portal returns a score. Plots and raw returns go into `outputs/weekNN/`. The README keeps live progress tables.

Changes I'd make to improve clarity and reproducibility:

- Split `bo.py` into modules: `surrogate.py` for the model classes (Gaussian Process, neural network), `acquisitions.py` for the seven scoring rules, `plot.py` for the diagnostic visualisations, `driver.py` for the per-round runner. Right now bo.py is around 700 lines — fine for one person, awkward for anyone dropping in cold.
- Add a `tests/` folder with smoke tests for each acquisition. Last week's neural-network failure (predicted 2.14, actual −17.92) would have been caught by a simple "does this scoring rule pick something sensible on a known surface" test before I deployed it.
- Move reflections out of `weekly/` into `docs/`. They're documentation, not part of the run.

Libraries and packages

Central to the approach:

- scikit-learn — Gaussian Process (the main predictive model), MLPRegressor (neural network surrogate), RandomForestRegressor (third opinion on feature importance), and the kernels. One library covers most of what I need.
- scipy — Sobol sampling (used to scatter candidate inputs evenly across the search box) and L-BFGS-B (the optimisation routine that fine-tunes the best candidates).
- numpy / pandas / matplotlib — standard data handling and plotting.
- jupyter — the weekly notebooks are the audit trail.

Trade-offs I considered:

The biggest one was scikit-learn vs PyTorch for the neural network. PyTorch would give exact gradients through the model rather than the finite-difference approximations I currently use. But it would add a heavy dependency for a network that is only ever fitting 13–43 points per function. sklearn's MLPRegressor is decent at this scale and the finite-difference gradients are quick. If the dataset ever grew to thousands of points, PyTorch would become the obvious choice.

I also chose to keep everything in one `bo.py` file rather than splitting things up front. At this stage that means one place to navigate — but as noted above, it's getting unwieldy and a split is overdue.

Documentation

The README already covers the basics: project purpose, inputs and outputs, search-box bounds, the eight functions, the technical approach, repo layout, quickstart, and a live progress table that gets a new row each round. It also has a "current best per function" table and a section mapping regression, SVM and iterative-modelling concepts from the course onto the actual project.

Updates needed to align with the most recent strategy and results:

- Add a "strategy evolution" section showing how the scoring-rule family grew round by round: W1 = UCB only, W2 = four explore-family rules, W3 = noise-aware EI, W4 = neural-net-driven probes, W5 = trust-gate plus model-free probes. Right now this story is buried in the weekly reflections; it deserves a top-level summary.
- Document the trust-gate logic in the technical-approach section: which functions are reliable, partial, or broken under the new leave-one-out R² check, and what scoring rule is chosen on each.
- Add a CHANGELOG so anyone reviewing can see when each new tool was added and why, without scrolling through six reflection files.

The bo.py docstrings are already plain-English, but the three additions from this week (`loo_r2`, `rf_importance`, `space_fill`) could each use a one-line usage example at the top of the file.