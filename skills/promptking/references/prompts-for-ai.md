# Prompt Results (when the deliverable is a prompt)

When the person asks for a prompt, system prompt or agent instructions, the prompt itself is the deliverable. Give a ready-to-paste prompt written to the standards in the official Anthropic, OpenAI, Google and DAIR.AI prompting guides (tagged per point below).

## What an expert prompt contains

Scale this to the task. A simple task gets a short, clear prompt; a production system prompt gets the full structure.

1. **Role and goal**: one or two sentences on who the model is and what success looks like. *(Anthropic, OpenAI)*
2. **Context and the reason behind constraints**: who the output is for and why each rule exists; reasons generalize better than bare rules. *(Anthropic)*
3. **Clear sections**: separate instructions, context, examples and input with consistent XML tags or Markdown headers, one style per prompt. *(Anthropic, OpenAI, Google)*
4. **Instructions in plain, direct language**: say what to do, numbered when order matters. Calm wording; no ALL-CAPS or "CRITICAL/MUST" pressure. *(Anthropic, Google)*
5. **Output format**: the exact structure, length and style expected, stated positively. Structured output or a JSON schema when code consumes it. *(Anthropic, OpenAI, Google)*
6. **Fallback for missing information**: what to do when the input lacks something (for example "write 'Not specified' for any owner or deadline not stated in the notes"). *(Anthropic, Google)*
7. **Examples, used with care**: one to three diverse examples with identical formatting when format or tone is hard to describe; zero-shot first for reasoning models. *(Anthropic, OpenAI, Google)*
8. **Input slot**: a clearly delimited `{{VARIABLE}}` placeholder; long material goes before the final instruction or question. *(Anthropic, Google)*

## Model-aware choices

- **Reasoning models** (current Claude, GPT and Gemini models think natively): give the goal and success criteria rather than scripted step-by-step reasoning; "think step by step" and forced `<thinking>` blocks add little or can hurt. Use them only for non-reasoning models. *(Anthropic, OpenAI, Google)*
- **Sampling parameters**: do not recommend temperature settings by default. Many current models ignore or reject them when reasoning is on. *(OpenAI, Google)*
- **No contradictions**: check that rules do not conflict; conflicts waste reasoning and degrade results. *(OpenAI)*
- **Multi-stage work**: when the task has distinct stages (extract, then analyze, then write), offer a short chain of prompts instead of one overloaded prompt. *(Google, DAIR.AI)*

## Context engineering (agents and long-running work)

- Include the smallest set of high-signal context; prefer references the agent can load on demand over pasting everything. *(Anthropic)*
- Write instructions at the "right altitude": specific about goals and boundaries, flexible about method. Prefer a few canonical examples to a long list of edge-case rules. *(Anthropic)*
- For long tasks: ask the agent to keep structured notes or progress files, and define when to stop or hand back. *(Anthropic, OpenAI)*
- Tool descriptions: one clear purpose per tool, no overlap, state when to use each. *(Anthropic)*

## Delivery format

1. The prompt in a single fenced code block, ready to paste, with `{{VARIABLES}}` marked.
2. One line on how to use it (where to paste it, what to fill in).
3. Optional: one line on an easy variation (for example a shorter version, or a stricter JSON output).

## Pitfalls

- A one-line prompt for a task that needs format and fallback rules, or a giant template for a simple task.
- Telling the target model to "think step by step" or setting temperature for a reasoning model.
- Missing fallback, which leads the target model to invent owners, dates or facts.
- Vague output spec ("summarize concisely") with no structure or length.
