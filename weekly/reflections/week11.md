# Week 11 reflection — BBO capstone

1. How past patterns shaped this round's choices
 

Two findings from the last fortnight now drive everything. The first is that the functions are repeatable: I've re-submitted an exact winning point twice now (functions 4 and 5, weeks apart) and both came back identical to a dozen decimal places. That converts every "best so far" from a possible to what I'm banking and what I will submit in the find round. It frees my remaining rounds for further searching.
 

The second is that careful beats bold, consistently. Every new best since week 8 — five of them — came from tiny steps near proven winners or from my one reliably-improving weekly rule on function 8. Every adventurous leap since week 4 has failed. So this round continues the formula: small steps where there's signal.
 

2. Clusters and recurring regions
 

Yes — three clear ones, each found differently.
 

Function 1 has a single tight hot spot. Four probes reveal a reading of −0.0053 at (0.41, 0.47), and readings between a hundred and a hundred-thousand times weaker at roughly 0.05 distance in three different directions. Whatever is there lives inside a box of about ±0.03 around that point. That's a cluster in the most literal sense — and this week's probe goes inside the box.
 

Functions 6 and 7 have plateau-like winning neighbourhoods. Small steps near their winners keep returning values within a whisker of the best (−0.263 vs −0.254; 1.819 vs 1.839). The good region isn't a single point, it's a small area.
 

Function 5's winner sits alone. Everything away from its corner returns values thousands of times smaller — the "cluster" is one isolated point, confirmed twice. The absence of any second promising region (I tested the opposite corner and three other quadrants) which hopefully means there is nothing else out there.
 

3. What proved less effective, and the adjustments
 

Three failures shaped the current approach. Predicting into unexplored territory failed every time I tried it — the neural network's suggestion in week 4, the partition process's optimistic pick in week 7, and my model's forecast in week 6 all over-promised badly. The adjustment: I stopped acting on any prediction more than a small step from observed data.
 

Wide exploration on the functions 1, 2 and 3 burned most of a season's queries for almost nothing. The adjustment: exploration now only happens where a live signal exists, or where it's free because the true peak is already banked.
 

4. The clustering parallel
 

My weekly routine has become a clustering algorithm. I group my historical queries by outcome — "winners", "near-winners", and "noise" — then treat each group differently: winners get banked exactly, near-winner neighbourhoods get explored with tiny steps, and the noise group gets abandoned rather than modelled. That's the same job a clustering method does: separate the meaningful structure from the background so effort goes where the pattern is. The partition process I built in week 7 makes the parallel explicit — it literally clusters past results into good and bad groups, then learns the boundary between them. 
 

5. What a plot would show, and what it tells me
 

Plot every query coloured by score and the portrait is stark. Functions 4, 6 and 7 would show a dense bright knot around each winner surrounded by scattered dim points — telling me to stay inside the knots. Function 5 would show one blazing corner and a dark everywhere-else — telling me it's finished. Function 1 would show a field of nothing with one faint smudge near (0.41, 0.47) — telling me exactly where the remaining two are going. Functions 2 and 3 would show no coherent grouping at all — dim points everywhere — telling me to spend nothing more there beyond banking their bests.
 