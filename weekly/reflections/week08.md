# Week 08 reflection — BBO capstone

How I used an LLM this week

My main engine is still a data-driven one (Gaussian Processes and a partition search), but this week I added a language model as a reasoning layer — specifically for the functions where my data-driven model is broken. On function 1 my model's trust check is negative (worse than guessing the average), so it can't tell me anything useful. That's exactly where an LLM reasoning from the plain-text brief might be useful.

1. Prompt patterns

I used both zero-shot and few-shot. Zero-shot meant handing the model just the function's brief ("radiation source detection, only proximity gives a non-zero reading, may have two sources") and asking where to probe. Few-shot meant also feeding it the actual history — all tried points and their scores — as worked examples. The structured, few-shot version gave more grounded suggestions but was over-cautious; the simplified zero-shot version was bolder and riskier. For function 1, where I just got my first non-zero reading (−0.0053 near (0.41, 0.47)), the few-shot version sensibly proposed a tight probe around that point to triangulate, rather than jumping somewhere unsupported.

2. Decoding settings

Using the model as an assistant, I don't get to touch a "temperature slider" directly, but I controlled the same thing through how I wrote the prompt. A tightly-scoped prompt with the data pinned down behaves like low temperature: safe, anchored, repetitive. An open-ended "what might be going on here?" behaves like high temperature: exploratory and more creative, but likelier to wander. I deliberately ran low-temperature-style prompting on functions I'm ready to bank (functions 4 and 7) and higher-temperature-style on the broken ones (function 1 — let it reason freely from the brief). Keeping the response short (a low max-tokens equivalent) stopped it rambling into unsupported speculation. That directly shaped function 1's query: the low-temperature framing kept the probe tight around the first bit of signal.

3. Token boundaries and unusual strings

The submission format — hyphen-separated values to six decimal places, each starting "0." — seemed to be mishandled by the LLM. The raw strings like `0.407463-0.465698`
, it occasionally dropped a decimal. I checked for this by validating every proposed string against the format rules programmatically before trusting it — the same validation my pipeline already runs. Token pressure isn't a problem at 17–47 points, but function 8's full history is getting longer.
4. Limitations observed

The clearest was attention fixating on irrelevant-in-aggregate context. Given function 1's full history, the model latched onto the single non-zero reading and effectively ignored the 16 flat zeros around it — the same over-confidence my numerical model falls into. I also hit diminishing returns from longer inputs: adding more historical points to the function 4 prompt didn't improve its suggestion.

5. Reducing hallucinations

Three concrete steps. I constrained the output format and validated it (zero invalid strings survived). I retrieved and fed the actual point history rather than letting the model invent values. And I gave tighter instructions — "stay within observed ranges, flag when you're extrapolating". The format constraint worked perfectly. The stay-in-range instruction was only partly effective: the model still over-predicted on function 4, exactly as my numerical model does, so grounding in data didn't fully cure the over-confidence.

6. Scaling

At larger scale I'd stop feeding raw points and instead feed summaries. The model's diagnostics (trust score, which inputs matter, current best) rather than hundreds of rows. For more complex models I'd retrieve only the most relevant past experiments, lower the temperature as the stakes rise, and tighten output constraints. Same principle as scaling my hide-one-point trust check to held-out chunks.

7. Thinking like a practitioner

The temperature dial is the explore-exploit dial I've been battling with all term. Low temperature is exploitation — trust the anchor near a proven winner. High temperature is exploration — reason freely where the data is useless. Choosing which to run per function, under a fixed query budget and incomplete information, is the challenge. If I had an infinite query budget I could just run a grid search, and then zoom in around any points identified.