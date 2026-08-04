Summary: Jones, Schonlau & Welch (1998), "Efficient Global Optimization of Expensive Black-Box Functions"
The problem
Some optimisation problems are easy because you can try lots of inputs cheaply and pick the best result. Many real-world problems aren't like that: each query is expensive — a crash test, a chemistry experiment, a simulation that runs overnight, an aerodynamics calculation that takes hours on a supercomputer. You might only afford 50 or 100 queries total. The standard "try lots of things and see what sticks" approach falls apart in that regime.

These problems also share another awkward property: you can't see inside the function. You give it numbers in, you get one number out, and that's it. No formula, no derivatives, no structure you can exploit. The paper calls these black-box functions.

The question the paper sets out to answer: given that each query is expensive and you have a limited budget, what is the most informative point to query next?

The key idea
The paper's recipe has two ingredients.

Ingredient 1: a model of the function. They fit what they call a "Kriging model" (these days usually called a Gaussian Process) to the points already queried. The model does two things at once: it predicts what the function's value is likely to be at any input you ask about, and it tells you how confident it is about that prediction. The further you are from existing queries, the less confident the model becomes. That uncertainty estimate is what makes the whole approach work.

Ingredient 2: a scoring rule for candidate next-queries. Once you have a model that gives both predictions and uncertainty, you can compute, for any candidate input, the expected improvement over the best score seen so far. A candidate is attractive if the model thinks it might score higher than your current best, weighted by how likely that is. Crucially, a candidate is also attractive if the model has no idea what the score there might be — because high uncertainty leaves room for a surprise upside.

Put those two together and you have a recipe:

Fit the model to whatever data you have so far.
Score every candidate input by its expected improvement.
Query the one with the highest score.
Update the model with the new result, and repeat.
The authors named this EGO — Efficient Global Optimization — and it's the algorithm that essentially everyone in this field still builds on today.

Why it works
The clever part is the balance built into "expected improvement". Two things drive a high score: the model predicting the point might be much better than the current best, or the model being very unsure about that point. The first behaviour leads to exploitation — refining around what already looks good. The second leads to exploration — testing parts of the search space we know nothing about.

A pure exploit strategy gets stuck on the first promising-looking spot, missing better peaks elsewhere. A pure explore strategy wastes queries on regions that are obviously low. Expected improvement gives a principled, automatic balance between the two — no manual tuning needed for the exploration-exploitation trade-off, because the rule does it for you.

The authors also prove a useful theoretical property: under mild conditions, the EGO algorithm will eventually find the true global maximum if you let it keep querying. That guarantee is stronger than most alternatives, which can permanently miss the global optimum.

What else is in the paper
Beyond the basic recipe, the paper covers practical concerns that anyone using the method in earnest runs into:

Choosing the kernel. The model needs an assumption about how "smooth" the function is. The paper explains the common choices and suggests sensible defaults.
Handling constraints. Real engineering problems often have constraints (the design has to be physically feasible, the cost has to stay under a budget). The paper extends EGO to handle constraints that are themselves expensive to evaluate, by fitting separate models to each constraint and modifying the scoring rule to account for the probability that the candidate is feasible.
Worked examples. The paper walks through several test functions, including a piston-design problem and a car-bumper crash simulation, showing how EGO finds good solutions in many fewer queries than the alternatives.
Comparisons. They compare EGO against the gradient-free optimisation methods of the time (DIRECT, multi-start hill-climbing, simulated annealing) on problems where each evaluation is genuinely expensive. EGO wins consistently.
What this paper changed
Before this paper, Kriging models (from geostatistics) and expected-improvement-style criteria (from earlier statistical decision theory) existed in separate corners of the literature. Jones, Schonlau & Welch put them together cleanly, named the resulting algorithm, made it practical, and demonstrated it on real engineering problems.

Modern "Bayesian Optimization" is essentially this paper's recipe with modernised vocabulary: "Gaussian Process" replaces "Kriging", "Acquisition Function" generalises "Expected Improvement", but the bones are the same. Every commercial hyperparameter tuner — Spearmint, GPyOpt, Google Vizier, Amazon SageMaker — descends from this algorithm. Every academic Bayesian Optimisation paper still cites it.

What I take from it for my own work
Three things shape my capstone strategy directly:

Treat the model's uncertainty as a first-class signal, not just its prediction. That's why I use Gaussian Processes throughout, not neural networks, which don't give calibrated uncertainty for free.
Trust the expected-improvement rule to balance exploration and exploitation automatically, without manually tuning a weight between the two. That's what I do whenever a function's model is reliable enough to follow.
Don't always chase the highest predicted value. The paper's argument that uncertainty alone is a good reason to query somewhere is exactly the justification for the informational probes I deploy when my model is uncertain.
