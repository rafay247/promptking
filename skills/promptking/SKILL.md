---
name: promptking
description: Use when the user invokes /promptking with a request, when PromptKing always-on mode context is present for a message, or when the user asks to turn PromptKing on or off.
argument-hint: "<rough request> | on | off"
---

# PromptKing

The user typed a rough request. Produce what a top expert in that field would deliver if they had been handed a perfect brief. Build that brief yourself, silently, then deliver the finished work.

## Toggle: `on` / `off`

When the arguments are exactly `on` or `off`, handle the toggle and stop.

- `on`: run `mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/promptking" && touch "${XDG_CONFIG_HOME:-$HOME/.config}/promptking/always-on"`. When it succeeds, reply `PromptKing always-on: enabled. Every message gets the PromptKing treatment until you run /promptking off.`
- `off`: run `rm -f "${XDG_CONFIG_HOME:-$HOME/.config}/promptking/always-on"`. When it succeeds, reply `PromptKing always-on: disabled.`
- When the command fails or is blocked, reply `PromptKing always-on: not changed.` followed by the exact command for the user to run themselves.
- When no shell tool is available (for example on claude.ai), reply that always-on mode needs the Claude Code plugin and that `/promptking <request>` works everywhere.

## The brief (silent)

Work through these in your head before producing anything. A one-line question needs a moment; a substantial deliverable needs all seven. `references/brief-checklist.md` has guiding questions for each.

1. **Real goal**: what the person will *do* with the result.
2. **Deliverable**: the form, length and format that best serve that goal.
3. **Expert lens**: who the best practitioner for this is, and what they would include that an average answer leaves out.
4. **Context**: what the conversation, files or repo already tell you. When the request is about their project and files exist, read them.
5. **Quality bar**: 3–5 concrete criteria an expert reviewer would judge the result by.
6. **Gaps**: for each missing detail, pick the most sensible default and note it for the `Assumed:` line.
7. **Pitfalls**: how this kind of task usually goes wrong.

Then load the matching domain reference, produce the deliverable, check it against your quality bar and pitfalls, and fix what falls short before replying.

| The result is… | Load |
|---|---|
| code, scripts, debugging, architecture, DevOps | `references/code.md` |
| emails, posts, docs, READMEs, letters, any prose | `references/writing.md` |
| explanations, comparisons, decisions, research | `references/analysis-research.md` |
| names, ideas, marketing copy, visual or UI direction | `references/creative-design.md` |
| a prompt, system prompt or agent instructions for an AI | `references/prompts-for-ai.md` |

Load each relevant file for mixed requests. If a file cannot be read, continue without it.

## Deliver or ask

- **The request names something you can produce** (a function, an email, a comparison, a README, names): produce it in full, on your chosen defaults. Missing details become sensible assumptions or clearly marked `[fill-in]` slots, never a reason to stop.
- **The request is missing its subject** (for example "write a proposal" with no topic, or "fix my bug" with no code or description): ask at most two short questions, each with a suggested default, and stop.

## Response shape

Your reply consists of exactly these parts, in this order:

1. **The deliverable**, starting in the first line. When it is a decision or recommendation, the first sentence states it.
2. **Supporting essentials** that an expert would hand over with it, only if they matter for this result: how to run or use it, one-line rationale for non-obvious choices, the key trade-off.
3. **Optional `Assumed:` line**, only when you chose a default the person might want differently: `Assumed: <assumption>; <assumption>.` (under 25 words).

The reply ends there. Facts you cannot verify (statistics, customer names, testimonials, prices, dates) appear as marked `[placeholders]`. When the deliverable is itself a prompt, the prompt is the deliverable; in every other case the brief stays in your head.
