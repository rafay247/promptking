# Research Notes — Official Prompting Guidance

All sources were fetched on **2026-11-16**. Points are paraphrased; quotes are kept to one short sentence. Model names are as they appear on the fetched pages.

## Sources

### Anthropic — Prompting best practices (Claude)

- URLs: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview (redirected from docs.claude.com), https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Start from success criteria and evals; prompting only fixes what prompts can control.
- Colleague test: if a smart colleague with minimal context would be confused by the prompt, Claude will be too.
- Be explicit about the action wanted ("change this function", not "can you suggest changes").
- Explain *why* behind an instruction; the reason generalizes better than a bare rule (e.g. "this will be read aloud by text-to-speech" instead of "NEVER use ellipses").
- 3–5 relevant, diverse examples in `<example>` tags; examples strongly shape behavior.
- Use consistent, descriptive XML tags to separate instructions, context, examples and inputs.
- Long inputs: documents at the top, query at the end (reported up to ~30% better on complex multi-document tasks); ask for relevant quotes first on long-document tasks.
- Formatting: say what to do rather than what to avoid; the prompt's own style pulls the output's style.
- A one-sentence role in the system prompt helps.
- Current models think by default (adaptive thinking, controlled by `effort`). Manual chain-of-thought is a fallback for when thinking is off; asking newer models to write reasoning in `<thinking>` tags "might be declined."
- "Think thoroughly" often beats a hand-written step-by-step plan when thinking is on.
- Aggressive language ("CRITICAL: You MUST…") and "if in doubt, use X" cause overtriggering on recent models; use plain "Use X when…".
- Newer models verify their own work; carried-over verification and anti-laziness instructions can cause over-verification or over-exploration.
- Risks named for recent models: overengineering (extra files, abstractions, defensive code) and test-gaming.
- Prefill on the last assistant turn is no longer supported on newer models; use direct instructions ("respond without preamble") or structured outputs.

### Anthropic — Effective context engineering for AI agents

- URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (published 2025-09-29)
- Context engineering is "the natural progression of prompt engineering": curating the whole set of tokens the model sees (system prompt, tools, data, history), repeatedly, not once.
- Goal: the smallest set of high-signal tokens that maximizes the chance of the desired outcome.
- Context rot: recall degrades as context grows; treat context as a finite attention budget.
- System prompts at the "right altitude": between brittle hardcoded if-else logic and vague guidance that assumes shared context.
- Minimal does not mean short — give enough to guide the behavior.
- Start with a minimal prompt on the best model; add instructions and examples to fix *observed* failures.
- Prefer diverse, canonical examples over a "laundry list of edge cases".
- Just-in-time retrieval: hold lightweight references (paths, queries) and load data when needed; progressive disclosure.
- Long-horizon techniques: compaction, structured note-taking outside the window, sub-agents returning condensed summaries.
- "Do the simplest thing that works."

### OpenAI — Prompt engineering, reasoning best practices, GPT-5 prompting guide

- URLs: https://developers.openai.com/api/docs/guides/prompt-engineering (redirected from platform.openai.com), https://developers.openai.com/api/docs/guides/reasoning-best-practices, https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide (marked archived), https://developers.openai.com/api/docs/guides/latest-model
- Durable rules in developer/system instructions; per-request input in user messages.
- Structure with Markdown headers and XML tags; order: identity, instructions, examples, context (variable context last).
- Reasoning models: avoid "think step by step"/"explain your reasoning" — it may not help and can hinder. Keep prompts simple and direct with high-level goals; a reasoning model is "like a senior co-worker."
- Zero-shot first; add examples only if needed, and for reasoning models examples must closely match the instructions.
- State explicit constraints and a concrete success criterion.
- Contradictory or vague instructions waste reasoning effort; removing contradictions "drastically streamlined" results.
- Over-eager context-gathering prompts caused needless searching on small tasks; calibrate eagerness and give stop criteria.
- For autonomous work: let the model make reasonable assumptions and document them rather than stopping to ask.
- Ask for Markdown only where it is semantically useful; control verbosity explicitly; state the main point early; use lists only for genuinely parallel or sequential content.
- Remove `temperature`/`top_p` when reasoning effort is on (latest-model migration guide).
- Style patterns to avoid listed by the latest-model guide: filler words like "delve", "leverage", "it's worth noting", and reflexive "X, not Y" framing.

### Google — Gemini prompt design strategies and thinking

- URLs: https://aistudio.google.com/docs/prompting-strategies (redirected from ai.google.dev), https://aistudio.google.com/docs/thinking
- Clear, specific instructions; explicit constraints (e.g. length) and an explicit response format; structured output for complex JSON.
- Recommends few-shot examples ("We recommend to always include few-shot examples"), with identical formatting across examples, but warns too many cause overfitting.
- Add grounding context and ask the model to answer from it.
- Decompose complex work: one prompt per instruction, chain sequential steps, or aggregate parallel ones.
- Thinking models already reason internally — "generally not necessary" to ask for planning or reasoning steps in the output.
- Keep temperature at default on earlier Gemini 3 models; Gemini 3.6+/4 ignore custom `temperature`/`top_p`/`top_k` and will reject them in future.
- Be "precise and direct"; avoid overly persuasive language; define ambiguous parameters; one consistent delimiter style per prompt.
- Put essential constraints, persona and output format in the system instruction or at the very start.
- Long context: supply all context first, put the specific question or instructions at the very end ("Based on the information above…").
- Use tools for recent facts and arithmetic.

### DAIR.AI — Prompt Engineering Guide

- URLs: https://www.promptingguide.ai/, https://www.promptingguide.ai/techniques, /techniques/zeroshot, /fewshot, /cot, /consistency, /react
- Technique catalog: zero-shot → few-shot (escalate when zero-shot fails); chain-of-thought (intermediate steps; zero-shot CoT via "Let's think step by step"); self-consistency (sample several reasoning paths, take the consistent answer); ReAct (interleave reasoning with tool actions and observations).
- Few-shot is "not a perfect technique" for complex reasoning; format and label distribution matter.
- CoT can hallucinate facts; ReAct depends heavily on retrieval quality.
- Note: many examples on the site target older non-reasoning models (e.g. `text-davinci-003`); vendor guidance above supersedes them for current reasoning models.

## Synthesis — principles PromptKing uses

1. **Define success before writing.** Know what a great result looks like and judge the draft against it. *(Anthropic, OpenAI)*
2. **Be explicit and direct; explain the why.** State the goal, the action and the constraints in plain language, with reasons. *(Anthropic, OpenAI, Google)*
3. **Right altitude.** Specific enough to steer, general enough to let a strong model use judgment; no brittle rule lists. *(Anthropic context engineering, OpenAI reasoning guide)*
4. **Separate parts clearly.** Delimit instructions, context, examples and input with consistent XML tags or headers. *(Anthropic, OpenAI, Google)*
5. **Long material first, question last.** *(Anthropic, Google)*
6. **Say what to do, not what to avoid** — especially for format and style. *(Anthropic, Google)*
7. **Examples with care.** Few, diverse, consistently formatted, closely matching the instructions; zero-shot first for reasoning models. *(Anthropic, OpenAI, Google, DAIR.AI)*
8. **Don't script reasoning for reasoning models.** Let native thinking work; ask for more effort rather than step lists. *(Anthropic, OpenAI, Google)*
9. **Calm language.** No ALL-CAPS or "CRITICAL/MUST" pressure; it overtriggers. *(Anthropic, Google)*
10. **No contradictions.** Conflicting instructions waste reasoning and degrade results. *(OpenAI)*
11. **Assume and document over stalling** when the task is actionable; ask only when blocked. *(OpenAI)*
12. **Decompose genuinely multi-stage work** into chained steps. *(Google, DAIR.AI)*
13. **Ground and verify.** Use provided context, tools or retrieval for facts; check results against the success criteria. *(Anthropic, Google, OpenAI)*
14. **Curate context.** Smallest high-signal set; just-in-time retrieval; compaction and notes for long agent runs. *(Anthropic context engineering)*
15. **Lead with the point; match format to content;** cut filler. *(OpenAI, Anthropic)*

## Advice we deliberately avoid

| Advice (from the earlier Gemini draft or common folklore) | What the sources say |
|---|---|
| Force a `<thinking>` block / "think step by step" in every prompt | Anthropic: manual CoT is a fallback when thinking is off; newer models may decline. OpenAI: may hinder reasoning models. Google: generally unnecessary for thinking models. Still valid for non-reasoning models. |
| Temperature 0 for deterministic tasks, 0.7–1.0 for creative | OpenAI: remove `temperature` when reasoning is on. Google: keep defaults on Gemini 3; ignored on 3.6+/4. Anthropic: depth is set with `effort`. Only relevant for older non-reasoning models. |
| ALL-CAPS "CRITICAL / MUST / NEVER" emphasis | Anthropic: causes overtriggering on recent models. Google: avoid overly persuasive language. |
| "Always" use few-shot / lots of examples | Google does recommend examples, but warns about overfitting; OpenAI says zero-shot first for reasoning models and examples must match instructions. We use examples selectively. |
| One mega-template for every prompt | Anthropic: "do the simplest thing that works"; right altitude; avoid laundry lists. Structure is scaled to the task. |
| "Never say don't" as a hard rule | Sources favor positive framing for format/style, but Google explicitly says to state what not to do when it matters. We prefer positive framing, not ban negatives. |
| Prefill the assistant turn to force a format | Anthropic: no longer supported on newer Claude models; use direct instructions or structured outputs. |
| Unverified "100x" quality claims | Every vendor: start from success criteria and evals. We measure. |
