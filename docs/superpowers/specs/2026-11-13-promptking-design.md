# PromptKing — Design Spec

**Date:** 2026-11-13
**Author:** Rafay Shaikh
**Status:** Approved in brainstorming, pending written-spec review

## 1. Goal

A person types a rough request and invokes PromptKing. Behind the scenes, Claude turns the request into an expert-level brief, executes that brief, and delivers **only the finished result** — measurably better than what the rough request alone would have produced.

PromptKing is a **result amplifier**, not a prompt rewriter. The enhanced prompt is an internal intermediate, never the deliverable (except when the request itself is "write me a prompt", in which case the prompt *is* the result).

### Non-goals (v1)

- No "deep" multi-pass mode (draft → critique → revise as separate passes).
- No subagent pipeline.
- No version for non-Claude tools (Cursor, ChatGPT custom instructions).
- No marketing claims (e.g. "100x") that the evals do not support.

## 2. User-facing behavior

| Situation | Behavior |
|---|---|
| `/promptking <rough request>` | Builds the hidden brief, executes, delivers the result. |
| Request is clear enough, or gaps can be filled sensibly | Proceeds without asking. |
| A wrong guess would make the whole result useless | Asks 1–2 sharp questions first, then executes. |
| A meaningful assumption was made | Appends one line: `Assumed: …` (omitted when nothing meaningful was assumed). |
| Trivial request ("what's 2+2", "thanks") | Answers briefly; the brief scales down to nothing. |
| `/promptking on` / `/promptking off` | Turns always-on mode on/off and confirms in one line. |
| Always-on mode enabled | Every normal message is handled as if prefixed with `/promptking`. |

The full enhanced brief is never printed.

## 3. Architecture

Single pass, inside the model's own reasoning: **Decode → Brief → Execute → Verify → Deliver**. Chosen over a subagent pipeline because it keeps full conversation context, adds no extra calls, and is fast.

### 3.1 Repository layout

```
promptKing/                          → github.com/rafay247/promptking
├── .claude-plugin/
│   ├── plugin.json                  plugin manifest
│   └── marketplace.json             lets users `/plugin marketplace add rafay247/promptking`
├── skills/promptking/
│   ├── SKILL.md                     lean core workflow
│   └── references/
│       ├── brief-checklist.md       the hidden enhancement, in detail
│       ├── code.md                  what "excellent" means per result type
│       ├── writing.md
│       ├── analysis-research.md
│       ├── creative-design.md
│       └── prompts-for-ai.md        prompt/context-engineering techniques, used when
│                                    the deliverable is itself a prompt
├── hooks/
│   ├── hooks.json                   registers the UserPromptSubmit hook
│   └── always-on.sh                 hook script
├── tests/test_hook.sh               hook tests
├── evals/
│   ├── cases.json                   the test prompts and expected behaviors
│   ├── judge_prompt.md              judging rubric
│   ├── run.py                       runs baseline vs skill, then blind judging
│   ├── test_run.py                  unit tests for the runner
│   └── results/                     raw outputs + summary (committed)
├── docs/superpowers/specs/          this spec
├── README.md
└── LICENSE                          MIT
```

### 3.2 SKILL.md (the core)

- **Frontmatter `description`:** states *when* to use it (the user invokes PromptKing on a request, or always-on mode is active, or the user asks to toggle it). No marketing language.
- **Body:** the five-stage workflow, the ask-vs-assume rule, the `Assumed:` line format, the `on`/`off` handling, and a routing table that says which reference file to load for which type of result. Target: under ~200 lines; detail lives in `references/`.

### 3.3 The hidden brief (`brief-checklist.md`)

Worked through silently for each request, scaled to its size:

1. **Real goal** — what the person will *do* with the result.
2. **Deliverable** — the form, length, and format that best serve that goal.
3. **Expert lens** — who the best practitioner for this is, and what they would do that an average answer would not.
4. **Context** — what the conversation, files, or repo already reveal; in Claude Code, read relevant files instead of guessing.
5. **Quality bar** — 3–5 concrete criteria an expert reviewer would judge the result by.
6. **Gaps** — for each: ask (only if a wrong guess wastes the work) or assume (and record for the `Assumed:` line).
7. **Pitfalls** — the typical failure modes for this kind of task (filler, invented APIs or facts, wrong versions, generic tone).

**Verify** re-checks the draft against the quality bar and pitfalls and fixes problems before delivering.

### 3.4 Reference files

Each domain file describes what separates an expert result from an average one in that domain (e.g. code: runs, handles edge cases, matches the existing codebase, no invented APIs; writing: audience-fit, specific, no filler). Content is grounded in the official guides listed in §6 and current-model behavior, avoiding outdated advice: no forced `<thinking>` blocks for reasoning models, no blanket temperature rules, no ALL-CAPS emphasis, few-shot examples used with care.

### 3.5 Always-on mode

- **State:** a flag file at `~/.claude/promptking/always-on`. `/promptking on` creates it, `/promptking off` removes it.
- **Hook:** `UserPromptSubmit` runs `always-on.sh`. If the flag file exists, it emits additional context telling Claude to apply the PromptKing skill unless the message is a slash command, a short acknowledgement, or an answer to a question Claude just asked. Otherwise it emits nothing. (Skipping is decided by Claude from that wording, so the hook needs no JSON parsing.)
- **Portability:** POSIX shell with no dependencies beyond standard tools. If the hook fails, the user's message goes through unmodified (fail open).

## 4. Error handling

- Missing or unreadable reference file → continue with SKILL.md alone; never block the response.
- Hook errors → fail open, no added context, no user-visible error.
- Asking means replying with the questions (each with a suggested default) and stopping; this works the same in interactive and headless runs.

## 5. Evaluation

- **Test set:** ~12 rough prompts covering code, writing, analysis/research, creative, "write me a prompt", at least one deliberately ambiguous request, and at least one trivial request.
- **Runs:** each prompt in a fresh headless Claude Code session, once without the skill (baseline) and once with it.
- **Blind judging:** a separate model call compares each pair in randomized A/B order against `rubric.md`: usefulness, correctness, specificity, fit to the unstated need, absence of padding. Headline metric: **win rate** for the skill.
- **Behavior checks:** asked when it should, did not ask when it should not, trivial answers stayed short, `Assumed:` line present only when appropriate, enhanced prompt never leaked.
- **Iteration:** revise the skill until the evals show a clear win; record final numbers in `evals/results/` and the README.

## 6. Sources

Fetched and verified during implementation (not the unverified video list from the earlier Gemini conversation):

- Anthropic — prompt engineering documentation and "Effective context engineering for AI agents".
- OpenAI — official prompting guides for current models.
- Google — Gemini prompt design strategies.
- DAIR.AI — Prompt Engineering Guide (technique catalog).

Each technique used in `references/` must trace to one of these. `README.md` lists them.

## 7. README requirements

Professional open-source README:

- Name, one-line tagline, badges (license, Claude Code plugin).
- What it does in two sentences; a real before/after example taken from the eval outputs.
- "How it works" diagram (Decode → Brief → Execute → Verify → Deliver).
- Installation: (1) Claude Code plugin marketplace, (2) manual copy into `~/.claude/skills/`, (3) upload to claude.ai as a skill.
- Usage: `/promptking <request>`, `/promptking on|off`, what the `Assumed:` line means.
- Benchmark results table with the real measured win rate and methodology link.
- Design principles, sources, contributing, license.

## 8. Repository & publishing

- Commits authored as **Rafay Shaikh <rafayf3@gmail.com>** (repo-local config); no Claude co-author trailer.
- The GitHub repo `rafay247/promptking` is created by Claude **at push time**; nothing is pushed until Rafay explicitly approves.

## 9. Open items to verify during implementation

- The exact invocation name of a plugin-namespaced skill (`/promptking` vs `/promptking:promptking`) and how to keep `/promptking` working for both plugin and manual installs.
- The current hook output format for `UserPromptSubmit` additional context.
- How to cleanly disable the skill for baseline eval runs in headless mode.
