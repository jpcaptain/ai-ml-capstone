# Week 05 reflection — BBO capstone

How I approached this week

Same recipe — fit a model, score candidates with an acquisition, query the highest. I added a check to see if the model should be trusted.

1. Hierarchical feature learning and strategy structure

Deep networks learn patterns in layers, each one building on the layer below. My approach has grown the same way: round 1 used a single scoring rule; round 2 split it into a family matched to each function's type; round 3 added a noise-aware version; round 4 added a neural network for predictions in unexplored regions. This week I added the something that should probably have been in place from round 1 — a check on whether to trust the model before letting it pick the next query.
Hide each known point, ask the model to predict it, see how close it gets. If the predictions are worse than guessing the average, I now ignore the model entirely on that function. That hopefully explains why three of my eight functions have been stuck for four rounds.

2. AlexNet-style leaps vs incremental tuning

AlexNet's win on ImageNet wasn't one magic breakthrough but several smaller improvements stacked together. My closest equivalent has been function 5: a different scoring rule plus a specific corner probe took the score from 1 089 to 8 662 in two rounds. Everything else has been small step by small step. This week's change was prompted by Omkar Joshi, as he mentioned a diagnostic in his discussion post that showed his model was actively misleading him on several functions. I added the same diagnostic into my own pipeline and found exactly the same pattern.

3. Depth versus efficiency, explore versus exploit

A deeper network can find richer patterns but takes longer to train and is more prone to fitting noise rather than signal. Exploring widely in my project is the same trade-off — more queries spent learning the landscape, slower to bank a confirmed win. Last week's neural-network bet on function 4 went wrong: I trusted the network's prediction in an unexplored region (it said 2.14, the actual return was −17.92).

This week I explicitly pulled back. Function 4 returned to the simpler scoring rule that gave it its previous win. The three "broken model" functions moved to a model-free probe that just spreads queries evenly across the search box.

4. Which neural-network ideas reframed my thinking

Cross-validation was the biggest this week — borrowed from Omkar to build the "trust gate". If the model can't predict its own training data after you hide a point, it isn't really learning, it's pattern-matching at random.

Gradients rank which inputs matter most to function 8: x3 and x1 dominate, x5 and x8 are nearly ignored.

Ensembles of models, even informal ones, are now part of my routine. For function 8 I run three independent methods (Gaussian Process, neural network, random forest) and only act on a signal where two or more agree.

5. Rapid prototyping vs structured production

I am firmly in rapid-prototype mode. This week alone I added three new tools and used them in the same submission. The cost of that speed showed up last week: I deployed a new scoring rule without checking whether its predictions in untested regions were sensible, and they weren't. I'm adding structure as I go, but the code still feels like it is evolving.

6. Real-world benchmarking — what does success look like?

A production deep-learning team cares about cost per prediction and consistency, not just chasing the highest score on a single benchmark. My eight functions now fall into three categories:

- Trustworthy Ish (functions 4, 5, 8) — the model is reliable enough to keep exploiting.
- Partial signal (functions 2, 6) — some signal but I need to keep exploring.
- Broken (functions 1, 3, 7) — the model is fitting noise, so don't ask it where to go; just spread queries out and look for a win.

Finally function 5's confirmed score of 8 662 is essentially a **safety net** — I know exactly where to submit in the final week to lock it in, so every week before then is a free chance to probe around looking for a higher value.