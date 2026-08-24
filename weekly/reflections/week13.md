# Week 13 reflection — BBO capstone (final round)

1. How the exploration–exploitation trade-off evolved


At the start of the project I treated the trade-off as a schedule: explore in the early rounds, exploit in the later ones. The data showed it is better treated as a per-function decision driven by evidence. In week 1, seven of the eight queries were exploratory. By the final rounds the position was not simply "mostly exploit" — it was full exploitation where the evidence was complete, and continued exploration where it was not. Function 5 was resolved by week 3, which made its weekly slot available for risk-free exploration from then on. Function 1 ran the other way: eleven rounds of near-zero returns, then a signal, and the final three rounds were spent following it — each step along one line returned roughly ten times the previous reading (−0.0053, +0.0027, +0.0315).


The balance also became asymmetric as data accumulated. With fewer rounds remaining, the cost of an unproductive exploration rose while its expected benefit fell, because fewer unknowns remained worth finding. Broad experiments gave way to small evidence-anchored steps.


2. Feedback and the parallel with Q-learning


Each weekly return updated two estimates: where value sits in the search space, and which actions are worth taking. The second is the Q-learning parallel. A reinforcement-learning agent maintains a value for each action and adjusts it after every observed reward. The equivalent here choosing the next action: "act on a long-range model prediction" began with a high assumed value, produced three substantial losses (weeks 4, 6 and 7), and was removed from the available actions. "Take a small step near a confirmed result" accumulated positive outcomes and became the main action. The weekly reliability check served as the update rule — it governed how much a new observation should shift confidence in each function's model, preventing a single result from swinging the strategy.


Function 1 illustrates the delayed-reward case. Seven consecutive rounds returned effectively zero, providing no reward signal. The eventual return — a reading that grew a hundred-fold once the active region was found. We managed to find this by maintaining the exploration throughout, and because each zero reading still carried information, progressively narrowing where the active region could be. This mimics the standard sparse-reward problem in reinforcement learning.


3. The AlphaGo Zero parallel — self-play, model-free and model-based


AlphaGo Zero improved by generating its own training data: each generation's games formed the next generation's input data. This project's loop had the same structure. Every submission was produced by the current strategy, and its result became the data that informed the next round's strategy.


On model-free versus model-based learning, the project used both, and the record shows clearly where each worked. The model-based approach, fit a model, anticipate outcomes, plan the query produced early results for functions 4, 5 and 8. The model-free approach, direct trial and error through small steps and simple probes, with no prediction attached was applied wherever a model failed its reliability check, and it produced most of the gains in the second half of the project. AlphaGo Zero's effectiveness came from combining learned evaluation with explicit look-ahead; the working equivalent here was combining model predictions with a check on whether those predictions had demonstrated accuracy and if not applying exploration and small-step probes.


4. Applying RL ideas to real-world optimisation


The clearest opportunity is to automate what this project did by hand. Each week involved three recurring decisions — how much attention each function deserved, how bold each query should be, and whether to keep spending on a function returning nothing. Reinforcement learning has an established mechanism for each.


Dividing budget across the eight functions is a multi-armed bandit problem. Allocating more activity to "arms" producing promising results and keeping a small set of activity for exploring those that are not. In a commercial setting the arms could be advertising placements or test variants competing for a fixed budget.


Query boldness: step sizes shrank as evidence accumulated — the practice of decaying exploration, applied in our project using judgement, could be applied via rules instead.


The most difficult case, a search that returns nothing for long stretches, is the sparse-reward setting. e.g. new drug detection. When to halt and when to persist.