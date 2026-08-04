# Week 06 reflection — BBO capstone

How I approached this week
 

Same recipe — fit a model, score candidates with a rule, query the highest. This week I extended last week's trust check into a trend-aware version: instead of looking at this week's R² alone, I track each function's history over all six rounds and decide based on both the latest value and the direction it's moving.
 

1. Progressive feature extraction
 

CNNs build features in stages — pixels become edges, edges become textures, textures become objects. Each layer abstracts further from the raw signal. My approach has done something similar with decision logic. Raw inputs feed the **Gaussian Process**; the model's per-input importance shapes my scoring-rule choice; that choice is filtered by the trust check (do I believe the model?); and this week the trust check itself is filtered by a trend layer (is the model getting better, worse, or stuck?). Multiple layers of decision-making now sit between eight raw inputs and one submission per function per week. That stacking is why I can confidently exploit function 4 while ignoring the model entirely on function 1 — different decisions at different layers.
 

2. LeNet-style leaps vs incremental tuning
 

LeNet was published in 1989 but didn't reshape computer vision until GPUs and ImageNet caught up twenty years later. My closest parallel is week 4's neural-network probes: a reasonable idea in principle, but at 13–43 points per function the network hallucinated rather than extrapolated. Last week's space_fill probes are the opposite — classical 1970s ideas that work because they don't assume the model knows anything. This week's biggest move was also classical: tracking how a measurement changes over time, treating one bad week as noise rather than signal. That improvement drove function 3's decision — its trust score jumped from broken to reliable in one week, but I held it at a conservative setting for one more week.
3. Depth, cost and overfitting vs explore vs exploit
 

The CNN trade-off — deeper network captures richer patterns but costs more and overfits more easily — maps almost perfectly onto BBO. A more aggressive scoring rule commits hard to one region; if the model is wrong, the query is wasted. Week 4 was my "too deep" mistake: a neural-net probe on function 4 said 2.14, actual return was −17.92. This week I'm consciously not over-committing. Function 4's model now scores +0.98 on the trust check and the rule predicts a big gain over the current best, but I chose the cautious scoring rule (EI, not PI). And on function 5 I'm deliberately probing the opposite corner (0,0,0,0) — five rounds in, the (1,1,1,1) peak is confirmed, but I'd never tested whether a hidden alternative might exist anywhere else in the cube.
 

4. Which CNN ideas reframed my thinking
 

Pooling was the most useful this week. Pooling combines local information into a summary that's robust to noise from any one source. My equivalent is the trend tracking I added today: instead of one week's R² driving the decision, I pool the last three weeks and look at the direction. That suppresses noise from any single week's data and reveals the trajectory. Function 3 was identified as "improving for five rounds running" rather than "lucky this week"; function 6 was identified as "oscillating between partial and broken" rather than the cleaner "stable" the single-week view would suggest.
 

5. Real-world benchmarking — Andrea Dunbar and edge AI
 

Andrea Dunbar's interview made the point that deploying CNNs on edge devices is about the best accuracy you can get within tight constraints on power, memory and time. My BBO equivalent is the one-query-per-function-per-week budget, leaving me with 5 submissions until the challenge is over. Success isn't "what's the highest possible score" — it's "what's the highest I can lock in given the 5 remaining goes".
 

That framing drove every decision this week. Function 5's confirmed peak at (1,1,1,1) is essentially a safety net — re-submittable in the final week — so intermediate weeks are a free chance to probe for alternatives. Function 3 was held back from full exploitation because committing now would waste future queries if the model has over-predicted. Function 7 was forced to space_fill despite a technically positive trust score.