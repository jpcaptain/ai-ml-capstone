# Week 10 reflection — BBO capstone

1. The reasoning behind this round


Three rounds left after this one, so every query now serves the final submission. The plan splits into three jobs.


The first is checking that what I've banked is real. Function 4 forced this up the schedule: last week a tiny nudge (one hundredth) away from its best point cost 0.23, while the previous week a *bigger* nudge cost only 0.03. When the loss doesn't track the distance, the function is either extremely jagged at fine scale or noisy — and if it's noisy, my banked 0.540 might have been partly luck. So this week function 4 gets its exact best coordinates re-submitted, as a straight reproduction test.


The second job is chasing live signal. Function 1's faint readings now bracket a hot spot — strongest at (0.41, 0.47), fading in both directions along the line I've walked — so this week's probe goes perpendicular to that line to close in from the other side. Function 2 finally improved after nine weeks (0.611 → 0.682), so it gets a careful probe near its new winner.


The third job is holding steady. Functions 6 and 7 keep their winners with only tiny variations, function 8 gets its usual free nudge (three marginal improvements in three weeks), function 5 explores cheaply because its true peak is already banked, and function 3 stays conservative.


The pattern from previous rounds driving all this: careful moves near proven points have delivered every recent win; bold leaps have failed for five straight weeks.


2. How transparent is my process?


More transparent than I expected when I started, mostly because I built the habit early. Another researcher picking up my repository would find: a README with a round-by-round progress table and the reasoning for each week's plan; a weekly notebook per round that generates the actual submissions; a reflection per week recording what I believed at the time and why; and a results file per round with the portal's returned values. Every function's full history — every point tried, every score returned — sits in one data file per function.


Could they reproduce my strategy? The mechanical parts, yes — the code is deterministic and each notebook regenerates its week's numbers. The judgement calls are documented but not mechanical: why I trusted one signal and not another lives in the weekly write-ups. What would they need that isn't written down, very little.


3. Assumptions I'm making


The big one: that each function gives the same answer if you ask twice. I've verified this for exactly one function (function 5, identical to fifteen decimal places). Everything else — including every banked best I'm planning to re-submit in the final week — rests on that assumption. Function 4's odd behaviour is the first real crack in it. If functions are noisy, my "best ever" values are partly lucky draws, and re-submitting the same coordinates might return less. That's why the reproduction test and the dress-rehearsal week exist.


A second assumption worth naming: that peaks are single points rather than plateaus. I refine with tiny steps because I assume the top is sharp — true for function 5, apparently true for 4 and 7, but function 6 near-reproduced at a small distance, suggesting its top is flatter. Where the top is flat, my tiny-step caution wastes queries.


4. Gaps and biases in my data


My sampling is heavily clustered. Early rounds chased corners (the exploration rules love corners because uncertainty is highest there), and later rounds clustered around winners. The middle of each search box is thin — function 5's interior got its first deliberate probe in week 7. There's also a survivor bias in what I refine: I concentrate where something good happened once, which the function 4 story shows can mean concentrating on a lucky draw.


5. One significant limitation


One query per function per week is the defining constraint, but the deeper limitation is what it does to verification. With so few queries, I've had to treat single observations as facts. Nearly every decision this term traces back to a number observed exactly once. A real experimental programme would replicate before believing, I've had to explore early on the belief that previous best results will hold.