# Transformers and decoding controls — reflection

> Discussion-board activity. Keep under 700 words.

## How temperature changes the output

Temperature is the clearest dial. At a low setting the model becomes almost robotic — it picks the single most likely next word nearly every time, so the same prompt gives the same safe, slightly repetitive text. It'll loop back on familiar phrasings and rarely surprise you. Turning it up flattens the odds: less-likely words get a real chance, and the output becomes more varied and creative, but past a point it tips into incoherence — grammatically shaky, wandering off topic. In the visualiser you can watch the probability bars even out as temperature rises: at low temperature one bar towers over the rest, at high temperature they're all roughly the same height, which is another way of saying the model is more unsure and willing to gamble.

The pattern that emerges is a straight trade-off between safe-and-repetitive and surprising-and-risky. There's no free lunch — you're choosing where on that line to sit.

## What top-k and top-p do

These two are guardrails rather than dials on the whole distribution. Top-k says "only ever consider the k most likely next words, ignore everything else". A small k (say 5) keeps the output tight and conservative; a large k opens the field. Top-p (nucleus sampling) is smarter about it — instead of a fixed number of candidates, it keeps just enough of the top words to cover a set share of the total probability (say 90%), so the candidate pool shrinks when the model is confident and grows when it's uncertain.

Restricting the candidates mostly protects coherence. Both top-k and top-p work by cutting off the long tail of very unlikely words — which is exactly where the model produces nonsense. So you can run a fairly high temperature for creativity but still keep top-p in place to stop the genuinely absurd words sneaking in. In practice top-p felt more natural than top-k, because it adapts to how sure the model is at each step rather than applying the same blunt cut everywhere.

## How this connects to attention

The decoding controls don't change what the model *believes* — attention has already done that work by the time we get to choose a word. In each transformer block, attention lets every word look back at the earlier words and decide which ones matter for what comes next. That's what produces the probability scores in the first place: if the earlier text strongly points at one continuation, attention concentrates the probability onto a few words and one bar towers over the rest. If the context is vague, attention spreads its focus and the probabilities come out flatter.

So the two mechanisms sit in sequence. Attention *assigns* the probabilities based on context; temperature and top-k/top-p then *decide how to sample* from them. The visualiser makes this visible — you can see attention concentrating on a key earlier word, and that focus is what makes certain next-words spike. Turning up temperature doesn't move the attention; it just makes the model more willing to pick from further down the list attention produced.

## Controlling behaviour, and the older-models comparison

The practical upshot: use low temperature and tight top-p when precision matters — factual answers, code, anything where one right continuation exists and a creative detour is a bug. Use higher temperature and a looser cut when you want range — brainstorming, drafting, creative writing — where a surprising word is a feature.

This is the same explore-versus-exploit trade-off I've been managing all term on my black-box capstone: low temperature is exploitation (trust the top prediction), high temperature is exploration (deliberately try less certain options). Same dial, different problem.

What makes transformers flexible here is self-attention. Older models read left to right through a fixed memory that faded as it went, so they couldn't easily re-weight the whole context for each new word — the decoding choice was stuck with whatever that fading memory offered. Self-attention rebuilds the full picture of what matters at every single step, so the probability list handed to the sampler is genuinely context-aware every time. That richer, fresher list is what lets these decoding controls do something useful rather than just shuffling a weak set of options.
