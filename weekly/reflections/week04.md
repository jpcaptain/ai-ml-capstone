# Week 04 reflection — BBO capstone

How I approached this
Same as last week — train a model on what I already know, score every possible next input, pick the highest. Two new ideas this week, both meant to stop me getting stuck on a local high instead of the real one:
A small neural network trained alongside the GP. It guesses the score in regions I haven't tried — places the GP basically gives up and reverts to its baseline.
Far probe rules (`far` and `nn_far`): predicted value × distance from points I've already tried. f4, f6, f7 all use the neural-net version — testing whether their earlier winners were a small isolated peak or the shoulder of a bigger one.




1. Edge points — where the surface changes fastest
Two big edges in the data:
- f5: (0, 0, 1, 1) returned 1 617; (1, 1, 1, 1) returned 8 662 — 5× jump between adjacent corners. A sharp ridge runs along the upper face.
- f7: my best gives 1.688; a nearby point drops to 0.053 — 30× drop. The winner is sitting on a cliff.




2. Did the neural net help find better directions?
Yes. I trained a small neural net on each function. For any point I can ask "if I nudge each input slightly, which way does the score climb fastest?" — that's the gradient.
For f4: at an unmapped point (0.08, 0.46, 0.69, 0.83), the net predicts **2.14** — nearly 4× my current best of 0.54. Lets see what we find.




3. If I treated this as classification — good vs bad
Label every known point "good" (top quartile) or "bad" (bottom quartile):
- Logistic regression: straight-line boundary. Fine for f5 (one good blob) but no good for f4, where the brief says there are several local highs.
- Non-linear SVM: curved or multi-region boundaries. The pick for f4 and f2.
- Neural network: most flexible, but with only 13-43 points per function would it memorise rather than learn.
When the classifier labels a point "bad" but it actually scored well (or labels it "good" but it actually flopped), that mistake usually happens right at the edge between the good and bad regions — So the mistake is telling me exactly where the boundary sits.
4. Which model felt most appropriate
For the main model, the GP still wins at this sample size — it tells me how sure it is, every scoring rule needs that, and it gives me per-input importance for free. Linear or logistic alone are too rigid.
The neural is useful as a different way of looking at things in empty regions — it extrapolates trends where the GP just defaults to baseline. 




5. Which inputs influence things most (f8)
Average influence per input on **f8** (8D, 43 points), highest to lowest:
`x3 (1.93) > x1 (1.82) > x4 (1.22) > x7 (1.12) > x2 (0.88) > x6 (0.78) > x5 (0.45) > x8 (0.33)`

x3 and x1 are the two most influential inputs on f8. The neural net's average sensitivity puts x3 first (1.93) and x1 second (1.82), with x8 at the other end basically being ignored. The GP independently agrees

6. Did the neural net give a useful boundary?
I didn't formally train a classifier this round — everything was a regressor. The idea works the same way though: the net's gradients are biggest exactly where the score changes fastest — which is where the good/bad boundary sits. The biggest gradients in my data sit at f5's corner peak and f7's Week 2 winner — the same edge points from Q1. 




7. Was the neural net worth the extra complexity?
On f8 (43 points): GP fit error = 0, NN fit error = 0.033 — both fit, both rank the same inputs as important. 
For deciding queries, the net's flexibility is useful as a second opinion. The f4 submission this week (net says 2.14 vs current best 0.54) is a bet. If its close to 2.14 it was worth it. If its near zero the net hallucinated. Either way, it useful information.