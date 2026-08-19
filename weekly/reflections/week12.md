# Week 12 reflection — BBO capstone

How the strategy has evolved

The first few rounds ran one rule for all eight functions and hoped for the best. Twelve rounds in, the weekly routine is systematic. Every Monday follows the same sequence: check whether each function's model can be trusted (hide known points, see if it predicts them), classify each function by what the evidence says it is — banked, live slope, faint signal, or dead end — and then apply the matching move: exact re-submission, a tiny step near the winner, a directional probe, or something systematic. The two reproduction tests were the most structured decision of the project: deliberately spending queries to prove the functions give the same answer twice, which allowed me to continue with the pattern of banking the best value to date for the final round submission. To ensure I don't lose anything, everything gets written down. What I chose, why, and what happened.

What drives the variation — my principal components

If I treat the whole history as one big data set, the striking thing is how few things explain most of the outcome differences. The first and biggest driver is simply distance from proven winners: small steps near a winner produce results within a whisker of it, and big leaps produce losses. That one "component" explains more of my results than everything else combined. The second is function character: rugged (functions 2 and 4, where even minute steps cost), plateau (6 and 7, where the winning pocket is forgiving) and sparse (1, nearly all zeros). Knowing which type I'm on predicts the outcome of a move better than any model I've built so far. And within function 8, three of the eight inputs drive nearly all the change while two are effectively ignored, which you could say is the clearest PCA-like structure in the project.

What to keep exploring, what to simplify away

After 12 rounds my rule has become: keep whatever still produces movement, drop whatever repeatedly hasn't.
So far dropped: predicting into unexplored territory (failed every time it was tried), wide exploration on the stubborn functions (a season's queries for nearly nothing), and medium-sized refinement steps (worst of both worlds on rugged ground).
Kept: pocket-stepping on functions 6 and 7 (three new bests between them), the weekly nudge on function 8 (five improvements in five weeks), and the signal chase on function 1 (which just produced the first positive reading of the whole project). That's the same logic as reducing dimensions: project the effort onto the few directions that carry the variance.

Into the penultimate round

This round is the last search; the next is the lock-in. Four functions (2, 3, 4, 5) are already decided — their final submissions are known coordinates with known, reproducible values, so exploitation there is total and exploration is zero. Four are still moving: function 1 gave me the 1st signal, I plan to explore close to it again this week. Functions 6 and 7 are still climbing, and function 8 improves every single week. So the penultimate submission, will be small exploration around all the best known results to-date.

What PCA teaches me about reading the results

First, focus on the variance: a handful of queries — function 5's corner, function 6's pocket discovery, function 1's box probe fit that description beautifully. Most of my hundred-plus queries individually moved nothing, which is the second lesson I draw from PCA: the low-variance directions aren't worthless, they tell you where the winners aren't: ruling out corners, quadrants and whole regions so I could zone in on certain areas. The final submission is all about dimensionality reduction: a hundred queries' worth of learning compressed into eight sets of coordinates.

