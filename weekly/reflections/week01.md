# Week 01 reflection — BBO capstone

How I approached this

Each function is a black box — I can't see its formula, only the handful of input / output points I've been given so far. The process is the same for all eight: fit a Gaussian Process (GP) to the known points (it predicts the output everywhere, plus how unsure it is), then use an acquisition function to score every candidate input and query the one that scores highest.

I built three acquisition modes so far and pick one per function depending on the stage:
- Explore — UCB with a high β: chase the most uncertain regions to map the space.
- Balanced — Expected Improvement (EI): trade off "might be high" against "unsure".
- Optimise — Probability of Improvement (PI): squeeze the area around the current best.

Early rounds I will Explore; later rounds shift toward Optimise as the picture firms up.
1. Main principle / heuristic per query point
_What guided each choice — exploitation of high outputs, exploration of uncertain regions, diversity of samples?_

My headline call this week was 'explore first, exploit later'. With only 10–40 points per function and no real idea what these functions look like, I didn't want to commit to a "best" spot yet — better to map the space for a few rounds first.

So for seven of the eight I used UCB with a high exploration weight (β = 3): it still leans toward areas the model thinks might be high, but it deliberately pushes into the uncertain gaps. In a bounded [0, 1] box those gaps are often the edges/corners, because that's exactly where I have no data yet — f3, f5 and f8 went to corners, which is intentional probing, not the model being sure it would get great hits.

The exception is f4, which I'm already exploiting with a balanced approach using Expected Improvement. There the model is genuinely confident an interior point beats my current best by a wide margin (predicts ≈ −1.8 vs best-so-far −4.0), so it would be silly to keep wandering instead of testing.

2. Most challenging function(s) and why
_Which were hardest to query and why? What additional information would have helped?_

f5 and the high-dimensional ones (f7, f8). f5 is supposedly a single smooth peak, but the model wants to hit a corner where it extrapolates the yield to ≈ 1639 (best so far ≈ 1089). That number is the GP guessing past the edge of its data, no evidence to support this — I'm sending the query there to learn. In 8D (f8) with 40 points everything is far from everything, so the model is unsure almost everywhere and exploration just heads to a corner.

What would have helped: knowing each function's real output range / whether there's a ceiling (so I'd know f5's 1639 is fantasy), the noise level of each function (for f2, a log-likelihood, I assumed some noise and let the model fit it — but I'm guessing), and a few seed points nearer the middle of the box so the model isn't extrapolating blind toward the edges.

3. Strategy adjustment for next round
_How will you adapt given current performance and uncertainty levels?_

Once this week's results come back, the corner gambles will tell me a lot. If f5's corner returns nowhere near 1639, that confirms over-extrapolation and I'll dial its β right down (or switch to EI) so it stays near known-good ground. More generally my plan is to explore: keep β high for another round or two to fill the space, then lower it and switch functions over to EI to start exploiting as the data fills in.

f4 is my test case for exploitation — if the predicted jump holds up, I'll tighten around there next round. And the rough rule I'm using for the moment: use exploitation where the model is confident and beats my best (f4-style), and treat any pick that lands exactly on a boundary as a test probe.
