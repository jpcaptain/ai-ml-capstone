# Retrospective — BBO capstone project

Retrospective on the BBO Capstone

Initial codebase

I built the codebase from scratch in Python, on top of scikit-learn and scipy, rather than adopting a specialist optimisation framework. The repository is public: https://github.com/jpcaptain/ai-ml-capstone


The rationale was scale and understanding. The problem sizes here — eight functions with between 10 and 40 starting points each, growing by one point per week — sit firmly in the region where scikit-learn's Gaussian Process implementation is sufficient. The heavyweight frameworks (BoTorch, GPyTorch) are built for GPU-scale problems and would have added dependencies without adding capability. More importantly, building each component myself meant I understood each decision the system made: when a query went wrong, I could trace why, which turned out to needed almost every week. The core grew into a single toolkit file (`bo.py`) holding the model, ten scoring rules, the diagnostics and the weekly driver, plus a second module (`partition_bo.py`) implementing a published competition method. Everything else in the repository, per-function data files, weekly notebooks, plots and written reflections forms the audit trail over the course of the project.

Code modification, week by week

The core loop never changed: fit a model to each function's history, score candidates, submit the best, learn from the result. Everything around it changed almost every week.

Weeks 1–2 moved from one exploration rule applied uniformly to a family of rules matched to each function's character; a variance rule for the sparse function, Thompson sampling for the noisy one, entropy search for the eight-input one. That change alone produced five new bests in week 2, including the project's single biggest result: function 5's extreme corner, which lifted its score from 1,089 to 8,662.

Weeks 3–4 expanded the toolkit; a noise-aware refinement rule, then a small neural network to suggest queries in unexplored regions. The network failed badly: it predicted 2.14 at a point on function 4 where the true value was −17.9. That failure drove the most important change of the project, in week 5: a weekly reliability check that withholds each known point in turn, asks the model to predict it, and bars any model that predicts worse than a simple average from directing queries. The check revealed that three of my eight models had been actively misleading me. Week 6 added trend-tracking on top, so one lucky week couldn't earn a model trust and one bad week couldn't destroy it.

Week 7 implemented the search-space partition method from the JetBrains NeurIPS 2020 competition entry — classify the space into good and bad territory, model only the good part. Its debut lost on all five functions it directed, but it pointed at the right areas, and one of its ideas ending up delivering results.

Weeks 8–12 consolidated into the process that produced most of the project's gains: very small steps near confirmed results, deliberate reproduction tests to verify that banked values were real, and directional probing wherever a live signal existed. Weeks 8 and 9 delivered five new bests between them. Week 11 was the best round of the project — four new bests, including the first positive reading on function 1 after eleven rounds of near-zero returns.

Two changes had the most significant impact: the reliability check (it changed which functions I would act on at all) and the week-8 switch from model-led search to small evidence-anchored steps (it changed how every remaining query was spent, and almost every subsequent gain came from it).

Final result

The last weeks were the strongest of the project. Weeks 11 and 12 produced six new bests between them, and the final submission converted the accumulated evidence into results: seven functions submitted their best-known coordinates, and function 1 — where three equal steps along one line had returned −0.0053, +0.0027 and +0.0315, roughly a tenfold increase per step — took one further step instead of banking. That final step returned 0.0481, 53% above the banked value, and was the right call.

The final scoreboard against the starting data: function 1 went from effectively zero to 0.048; function 4 from −4.03 to 0.540; function 5 from 1,089 to 8,662; function 6 from −0.71 to −0.15; function 7 from 1.37 to 1.86; function 8 from 9.60 to 9.95. Functions 2 and 3 finished near their seed values.

With a fresh start I would change three things. First, I would run repeat queries at identical coordinates on every function in the opening weeks. The final round revealed that only four of the eight functions are deterministic — functions 2, 3 and 6 return different values at the same inputs — and I discovered this in the last submission, having generalised from two reproduction tests to all eight functions. Knowing which functions are noisy from the start changes the strategy. Second, I would introduce the reliability check in week 1 rather than week 5; the first month spent a lot of budget on the advice of models that the check would have disqualified. Third, I would cut the broad exploration phase short on the functions that showed nothing — functions 1, 2 and 3 consumed most of a season's queries before strategy changed, and the eventual function 1 breakthrough came from patient local triangulation, not from the wide search.

Trade-offs and decisions

The defining trade-off was set by the budget: one query per function per week, every query permanently spent. Within that, three tensions informed every round.

Exploration versus exploitation I eventually stopped treating as a schedule and started treating as a per-function state. Each week, every function was classified by its evidence — verified, improving, localising, or no reliable signal — and each state had a defined action. Function 5 was resolved by week 3, so its slot became free exploration for the rest of the project. Function 1 stayed in exploration for eleven rounds because nothing was proven, then flipped to pure pursuit when a signal appeared.

Verification versus performance was the least obvious trade-off and the one I most value in hindsight. I spent a couple of queries deliberately re-submitting known coordinates — three reproduction tests in total — that could never improve a score. They bought certainty: they established which results were bankable, converted the final round from I think this will be the result into a guarantee for the deterministic functions. Unfortunately I happened to test deterministic functions and so in the final round I discovered there were several noisy functions.

Sophistication versus simplicity was resolved by the results. The neural network, the partition method's bold picks and the model's own long-range forecasts all underperformed; small steps near confirmed winners produced eleven of the project's new bests. At 20–50 data points per function, simple moves anchored in evidence beat clever moves anchored in models.

Learning and application

The most important lesson: a model must earn the right to be believed, and the test doesn't cost any queries. Withholding known data points and checking whether the model can predict them costs nothing but compute, and it changed my results more than any modelling improvement. Every damaging decision of the project — the week 4 neural network loss, the week 6 forecast failure, the week 7 partition losses came from acting on a prediction that had never been validated in the region it was predicting about.

This applies directly to my work in media, where I focus on content recommendation, subscriber retention and advertising placement. The same problem exists there: a churn model or a recommender produces a score, the business acts on it, and no one has checked whether the model is actually accurate for the customers it is scoring. The working habits from this project carry straight across: test a model before acting on its output, keep a proven option in place before trying a new one, spend part of the budget on checking results rather than only chasing new ones, and record each decision and the reason for it. The budget lesson holds as well: a live test on a real audience, like a portal query, can only be run once.

Two things surprised me. The first was how often model predictions failed in regions where there was no data. Every method I tried — the neural network, the partition model and the Gaussian Process itself — predicted values in untested areas that turned out to be wrong, across different weeks and different functions. The models were reliable for estimating values close to existing data and for showing where uncertainty was high, but not for predicting far from what had been observed. The second surprise was how much I gained from other participants. The weekly reliability check that shaped the second half of my strategy came from a diagnostic another participant described in a discussion post, and the partition method came from a paper referenced in another. My results improved because I read what others were doing, and that is probably the most useful habit to take forward.