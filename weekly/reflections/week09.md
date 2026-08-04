# Week 09 reflection — BBO capstone

How I approached this week

Last week was my best round since week 2 — three new bests, all from careful moves near proven winners rather than bold leaps. With four rounds left before the final submission, this week continues that shape: refine where there's live signal, keep everything else moving toward a confirmed final answer.

1. Scaling laws and my query choices

Scaling laws describe how performance improves as you add resources — and the striking thing is how differently my eight functions "scale" as data accumulates. Function 8 is the textbook case of diminishing returns: 9.60 → 9.89 → 9.95 → 9.9499 over six rounds, each gain roughly a tenth of the one before. More queries still buy improvement, but the price per unit keeps rising. Function 4 tells a similar story — it has plateaued around 0.54, and last week even a whisker-sized nudge away from the peak cost me 0.03.

But the returns aren't uniformly diminishing, and that's the important lesson. Function 6 sat flat for six weeks and then jumped from −0.705 to −0.254 in a single query. Function 7 did the same: +0.15 in one week after a month of nothing. So my scaling curve isn't a smooth line — it's long flat stretches punctuated by steps. That shapes the strategy: I use queries where a step just happened (functions 6 and 7 this week), and further exploration where the curve has genuinely flattened.

2. Emergent behaviour

The clearest emergent surprise in my project: function 1 produced its first meaningfully non-zero reading in week 7, after seven rounds of dead-flat zeros. Nothing about the previous data predicted it — and it instantly changed the plan for that function from "spread queries and hope" to "triangulate the signal". Last week's follow-up probe found the signal fades toward the centre of the box, which gives me a direction to chase this week.

That experience is why I'm careful about declaring any function finished. A flat history doesn't prove a flat function — it may just mean I haven't stepped on the interesting part yet. So I've built the plan as follows: a small number of queries are kept for exploring even in these final weeks, and I never spend the whole week's query allowance on polishing alone.

3. Cost, robustness, performance

All three are in tension now. Cost is fixed and get more expensive with every week — one query per function per week, four rounds left. Performance says chase new bests. Robustness says make sure the bests I already have are actually repeatable.

The robustness point matters more than it looks. Only one of my eight functions (function 5) is confirmed to give the same answer twice — I re-submitted its winning point and got an identical value to fifteen decimal places. Every other "banked" result has been observed only once. So my plan reserves the week before the final as a full dress rehearsal: submit exactly the coordinates I intend to use in the final week, and find out a week early if any of them don't reproduce. That's one entire round of potential performance deliberately spent on robustness — and after watching a confident prediction miss by a mile in week 6, I think it's a useful trade.

4. Balancing predictable gains against sudden ones

My answer is a portfolio. Six of this week's eight queries are predictable-gain moves: tight refinements around last week's new winners on functions 6 and 7, careful probes close to each function's best-known point elsewhere, and the reliable weekly nudge on function 8. Two are bets on surprise: function 1, where I'm following the direction the faint signal points, and function 5's keep exploring (its true peak is already banked, so exploring there costs nothing).

The black-box constraint is what forces this discipline. I can't see the surfaces, so I can't know which flat function is hiding a step — I can only price the bets. Refinement near a proven winner has a known, modest upside and almost no downside. Exploration has unknown upside and a known cost of one query. With four weeks left, the maths says: mostly bank, keep a few lottery tickets.