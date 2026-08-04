# Datasheet — BBO capstone query history

*Following the datasheet-for-datasets framework (Gebru et al.). Covers the query history and function evaluations collected during Stage 2 of the BBO capstone, weeks 1–10.*

## Motivation

**Why was this data set created?** To support a black-box optimisation challenge: eight unknown functions, each taking between 2 and 8 inputs in the range 0 to 1, each returning a single score. The goal is to find inputs that score as high as possible. Every data point is one real query against the course portal — the data set is the search history.

**What task does it support?** Fitting the models that propose each week's queries, checking whether those models deserve trust, and (at the end) proving where the best-known point of each function lies and how it was found.

## Composition

**What does it contain?** One file per function (`data/f1.csv` … `data/f8.csv`). Each row is one query: the input values (`x1` … `xd`) and the returned score (`y`). The first rows are the seed points provided by the course; every row after that is one weekly submission, in order.

**Size and format.** Plain CSV. As of week 10: between 19 points (functions 1 and 2) and 49 points (function 8), a little over 250 rows in total across all eight files. Two supporting files: `function_descriptions.csv` (the portal's plain-text description of each function) and `r2_history.csv` (a weekly record of how trustworthy each function's model was).

**Are there gaps?** Yes, and they're worth calling out. The sampling is clustered — early rounds favoured the corners of each search box, later rounds clustered around known winners, and the middles are thin. Function 5's interior wasn't deliberately probed until week 7. Almost every value has been observed exactly once, so the data can't tell you how repeatable any single reading is (the exception is function 5, whose peak was re-queried and reproduced exactly).

## Collection process

**How were the queries generated?** By a weekly optimisation loop: fit a model to each function's history, score candidate inputs with a scoring rule chosen per function, submit the best candidate, record the portal's returned value. The scoring rules evolved over the ten rounds — from a single exploration rule in week 1, through a family of specialised rules, to a trust check that decides each week whether the model should be believed at all. The full week-by-week story is in the README's progress table and the weekly reflections.

**Over what time frame?** One round per week, from late May to late July 2026. One query per function per round — the defining constraint of the whole exercise.

## Preprocessing and uses

**Transformations?** None on the stored values — the CSVs hold exactly what was submitted and exactly what came back. Inside the modelling code, inputs are rescaled to a 0–1 box and outputs are standardised before fitting, but those transformations are applied on the fly and never written back to the data.

**Intended uses.** Reproducing this project's strategy; teaching examples for sequential optimisation under a tight budget; benchmarking alternative strategies against the same history ("what would rule X have proposed in week 5?").

**Inappropriate uses.** Drawing conclusions about the true shape of the eight functions beyond the sampled regions — the coverage is too thin and too biased for that. Treating single observations as reliable estimates — most values were measured once, and at least one function (function 4) shows signs of noise or extreme ruggedness.

## Distribution and maintenance

**Where is it available?** In the public GitHub repository for this capstone, alongside the code that generated it.

**Terms of use.** Free to use for study and research with attribution. The underlying functions belong to the course; this data set only describes where I probed them and what came back.

**Who maintains it?** Me (JP Camelbeek). It grows by eight rows per week until the final submission, after which it is frozen as the project record.
