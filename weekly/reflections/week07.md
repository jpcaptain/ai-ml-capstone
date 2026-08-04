# Week 07 reflection — BBO capstone

How I approached this week

I made a big change this round. I built a second, separate process based on the JetBrains NeurIPS 2020 competition entry — it splits the known points into "good" and "bad" by score, trains a classifier to learn where the good territory sits, zooms in, and only searches inside it. Five of my eight submissions came from that process this week. The other three stayed with my existing toolkit.

1. Which settings I tuned and why

The new partition process has three settings that matter: how deep to zoom (capped at five levels), how flexible the boundary can be (too rigid misses oddly-shaped good regions, too flexible draws boundaries around noise), and the minimum number of points a region needs before it's worth zooming further. I spent most care on the minimum-points rule — my datasets are tiny, between 16 and 46 points per function, and a split based on a handful of points is really just guessing.

2. How tuning changed my query strategy

It moved five of my functions from "wander around and probe" to "refine near known winners". Function 7 is the clearest example: four weeks of exploration rules got me nothing, and then the partition process proposed a point right next to my best-ever result. Function 8 tells a similar story — my previous rule had settled into proposing the same point every week, and the partition broke that habit with a genuinely different candidate, one that also tests a hunch two other methods had flagged (that input 5 should be high). In short, tuning shifted me from breadth to focus.

3. Which tuning methods I used and the trade-offs

I ended up using three approaches at different levels. I tuned the strategy-level settings by hand, which is quick and lets me use judgement, but it's ad hoc and hard for anyone else to reproduce.

The model itself does its own automatic tuning — every week it re-fits its smoothness and noise settings from scratch, restarting ten times to avoid a bad fit. That's reliable, but the compute cost grows as the data does.

The trade-off I felt most sharply: a proper grid search over my partition settings would have been more rigorous than my hand-picked values, but every evaluation of a setting costs a real portal query I can't get back. So judgement had to stand in for search.

4. What the growing data reveals

Three limitations have come into focus. Some functions simply can't be modelled yet — on function 1 (16 points), my weekly trust check shows the model predicts held-out points worse than just guessing the average, and more data hasn't fixed it because the surface is nearly all flat zeros.

Some inputs turn out to be irrelevant — on function 8, three independent methods agree that two of the eight inputs are being ignored, probably because they're categories disguised as numbers.

And returns are diminishing — function 8's score has crawled from 9.60 to 9.95 over six rounds, each query buying less than the one before.

5. Applying this to larger data and future projects

Two things carry forward directly. The first is using the optimiser to tune the optimiser: my partition settings were hand-picked, but with more budget I'd tune them with the same Bayesian machinery — which is exactly what the JetBrains team did.

The second is about scale: my hide-one-point trust check gets too slow on large datasets, and the standard fix is to check against a few held-out chunks instead.

For future deep-learning work, the tournament pattern applies too: screen lots of settings cheaply with short training runs, and only promote the survivors to full runs.

6. Thinking like a practitioner

What this set-up really teaches is a set of working habits. Don't act on a model until it has earned trust — I no longer follow any suggestion from a model that fails its weekly check. Price every query against what it might teach you. Keep a fallback, e.g. if you have a high point keep searching in case it a local optimum. And write the decisions down: every rule choice, the reasoning behind it, and what happened next. Real ML work looks exactly like this.