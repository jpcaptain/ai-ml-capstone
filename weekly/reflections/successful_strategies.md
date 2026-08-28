# Successful optimisation strategies — reflection

The strategies behind my strongest results

Four strategies account for nearly all of my results, and each earned its place by evidence rather than by design.

Classifying functions by evidence state, and matching the strategy to the state. From mid-project onward, every function was placed each week into one of four states — verified, improving, localising, or no reliable signal, with a defined action for each. This mattered because the eight functions turned out to be fundamentally different problems: one had a sharp corner maximum, two had forgiving plateaus, one was almost entirely flat, three turned out to be noisy. A single strategy applied uniformly performed poorly in the opening rounds for exactly this reason. The classification influenced everything downstream: it decided where the weekly budget went, how bold each query could be, and when a function could move into free exploration.
A reliability check before any model was believed. From week 5, each function's model was tested weekly by withholding every known point in turn and asking the model to predict it; any model that predicted worse than a simple average was barred from directing queries. This was the highest-impact change of the project. It exposed that three of my eight models were actively misleading, and it explains the before-and-after pattern in my results: every damaging decision (weeks 4, 6 and 7) came from acting on an unvalidated prediction; almost every gain after week 8 came once the gate was in place.

Small steps near confirmed results. Eleven of my new bests came from queries placed within 0.02 of an existing best, including the improvements on functions 6 and 7 in weeks 8 and 11, and function 2's only improvement of the project. The effectiveness has a simple cause: at 20–50 data points per function, models interpolate well and extrapolate badly, so the reliable information is concentrated near observed points. Once the pattern was visible in the data, it changed my decision rule: no query was placed more than a small step from evidence unless its purpose was explicitly exploratory.

Deliberate verification queries. I spent several queries re-submitting known coordinates. They established which results were bankable, they converted the final submission from a theory into a guarantee for the deterministic functions, unfortunately I discovered too late that not all the functions would return the same answer given the same input.

Two individual decisions deserve mention alongside the systematic strategies: the week 2 corner submission on function 5 (combining the brief's "single peak" description with the model's boundary-pointing behaviour; 1,089 → 8,662, the largest single gain of the project) and the closing decision on function 1 to take one further step along a rising signal rather than banking the guaranteed value — which returned 53% more than the banked figure.

What defines a successful strategy

Outcomes are necessary but not sufficient. My view after thirteen rounds is that a successful strategy has five properties, and the leaderboard only measures the first.

Outcomes, obviously — six of eight functions materially improved.
But adaptability is what produced those outcomes: my strategy in week 12 shared almost nothing with week 1 except the core loop, and every change was a response to observed results rather than a plan I had laid out in advance.
Reasoning quality matters independently of results, because the sample sizes are too small to distinguish luck from skill by outcomes alone. The corner gamble on function 5 succeeded and the neural-network gamble in week 4 failed, but what actually separates them is that one combined two independent sources of evidence and the other rested on a single unvalidated model.
Verifiability, is also important. Can the result be reproduced on demand or was it a fluke set of circumstances that aligned to give the result. The final round proved this concretely — the "best observed" values on my three noisy functions were partly luck.

Efficiency, especially when the cost per experiment is high is probably the best measure of how well a strategy is working. Anyone can run a grid search given enough time and compute, but deploying the best tests to gain the maximum amount of information per query is vital.

Application beyond the capstone

The capstone has the same structure as many applied data science projects: tests are expensive, the budget is limited, and information is incomplete. In my field — media, working on content recommendation, subscriber retention and advertising placement — the parallels are straightforward. An audience test costs real exposure and takes real weeks, just as a portal query cost a round.

The same working practices apply. Check a model against held-out data before acting on its scores — a churn model's output is only useful once it has been tested against customers who actually churned. Keep a proven option in place before trying a new one — a new ad policy should not go live without the existing one ready to restore, and the new model needs to outperform on existing data, otherwise the cost of change is not justified.
Understand whether a system gives consistent or variable results before trusting a single measurement — one good week for a test variant is not a result, a lesson my three noisy functions taught me late. And record each decision and the reason for it, because over a long programme that record is what allows you to build a more effective strategy, and allows others to follow and learn from the work.

Peer strategies — what worked, and where we overlap

The peer whose work most influenced mine was Omkar Joshi, and two of his practices became part of my toolkit. The first was his leave-one-out diagnostic: checking whether each function's model could predict data points it had not seen. He reported that several of his models failed this test. I ran the same check on mine, found the same problem, three models predicting worse than a simple average, and this became the weekly reliability check that shaped the rest of my project. The second was his use of agreement across independent measures: he ranked input importance four different ways and only acted where the methods agreed. I built a three-method version for my eight-input function, and it correctly identified the two inputs that carry no signal.

One of his observations also produced a useful negative result for me. He found that a high value of one particular input worked well on his function 8. I tested the same idea on mine in week 7 and it clearly failed (9.03 against my existing 9.95).

Dr Matthew Harper took a different route to the same principle: instead of trusting one model, he ran several, multiple model configurations selected by cross-validation, a blend of scoring rules, and a separate neural-network suggestion as a cross-check and acted with most confidence where they agreed. Loukia Kritioti did something similar with scoring rules, comparing the suggestions of several and treating agreement as a signal. My approach was a bit more simple, one model with a reliability check, which I think suited the small data sizes in this project.

Suggestions, and what my peers changed in my thinking

I would offer two suggestions. First, to those running ensemble and consensus approaches: add deliberate repeat queries. Agreement between models tells you a prediction is stable, but only re-querying the same point tells you whether the function itself is stable — and my final round showed that difference matters for knowing which results you can rely on. Second, an observation from looking through peers' repositories: documented code is helpful, but documented decisions, which rule was chosen each week, why, and what happened are just as valuable.

My peers also changed how I think about success. Yiqun Huang made the point mid-course that a query can be worthwhile for what it teaches even when the score does not move, and judged his weeks partly on information gained. I came to score my own rounds the same way: several of my most useful queries produced no improvement at all, and my function 1 result only exists because eleven scoreless rounds were treated as information rather than failure. Between his framing, Omkar's diagnostics and the ensemble builders' caution about single models, both my process and my end results improved.