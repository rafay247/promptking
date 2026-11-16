# PromptKing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship PromptKing, a Claude Code plugin whose skill turns a rough request into an expert-quality *result* (not an enhanced prompt), with an optional always-on hook, a measured eval, and a professional README.

**Architecture:** One plugin repo. The skill (`skills/promptking/SKILL.md`) runs a silent Decode → Brief → Execute → Verify → Deliver pass and loads domain reference files on demand. A dependency-free `UserPromptSubmit` hook injects an "apply PromptKing" note while a flag file exists. A Python runner compares baseline vs skill outputs from headless `claude -p` runs and has a blind judge pick winners.

**Tech Stack:** Claude Code plugin format (`.claude-plugin/plugin.json`, `marketplace.json`, `hooks/hooks.json`), Markdown skills, POSIX `sh` hook, Python 3 stdlib (`unittest`) for the eval runner, Claude Code CLI 2.1.x.

## Global Constraints

- Commits authored as `Rafay Shaikh <rafayf3@gmail.com>` (already set in repo-local git config). **No `Co-Authored-By: Claude` trailer, no Claude attribution anywhere.**
- **Never push** and never create the GitHub repo until Rafay explicitly approves (Task 9).
- The enhanced brief is never shown to the user; output is the result plus an optional single `Assumed: …` line.
- Ask only when a wrong guess would make the whole result useless; at most 2 questions.
- No unverified claims (no "100x"). README numbers come only from `evals/results/` of the final run.
- Every technique in `references/` must trace to a source in `docs/research-notes.md` (Anthropic, OpenAI, Google, DAIR.AI).
- Avoid outdated advice: no forced `<thinking>` blocks for reasoning models, no blanket temperature rules, no ALL-CAPS emphasis, careful use of few-shot.
- Hook must fail open and use no dependencies beyond POSIX `sh`.
- Flag file path: `${XDG_CONFIG_HOME:-$HOME/.config}/promptking/always-on` (changed during Task 5: `~/.claude` is a guarded path, so writes there were blocked).
- `SKILL.md` stays under ~200 lines; detail goes in `references/`.
- License: MIT, copyright "Rafay Shaikh".

## Verified facts (probed on this machine, Claude Code 2.1.220)

- A plugin skill named `promptking` in plugin `promptking` is invocable as both `/promptking <args>` and `/promptking:promptking <args>`.
- `UserPromptSubmit` hook stdout `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"…"}}` reaches the model.
- `claude -p --setting-sources project` excludes the user's personal plugins (only built-in skills remain); `--plugin-dir <repo>` adds PromptKing; `--disable-slash-commands` removes all skills.
- Pass `stdin=/dev/null` to `claude -p` to avoid a 3-second stdin wait.
- `claude plugin eval` is early access and not enabled for this account, hence the custom runner.

## File Structure

| Path | Responsibility |
|---|---|
| `docs/research-notes.md` | Verified source notes: URLs, key points, synthesis, advice we avoid |
| `docs/baseline-observations.md` | How baseline (no-skill) outputs fall short, per eval case |
| `.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Single-plugin marketplace so users can install from the repo |
| `hooks/hooks.json` | Registers the `UserPromptSubmit` hook |
| `hooks/always-on.sh` | Emits the PromptKing context when the flag file exists |
| `tests/test_hook.sh` | Hook behavior tests |
| `skills/promptking/SKILL.md` | Core workflow, toggle handling, output rules, routing table |
| `skills/promptking/references/brief-checklist.md` | The 7-point hidden brief in detail |
| `skills/promptking/references/code.md` | What separates expert code results |
| `skills/promptking/references/writing.md` | … writing results |
| `skills/promptking/references/analysis-research.md` | … explanations, comparisons, decisions |
| `skills/promptking/references/creative-design.md` | … naming, ideas, copy, visual direction |
| `skills/promptking/references/prompts-for-ai.md` | Prompt/context-engineering techniques, for when the deliverable is a prompt |
| `evals/cases.json` | 13 rough test prompts with expected behaviors |
| `evals/judge_prompt.md` | Blind pairwise judging rubric (the spec's `rubric.md`) |
| `evals/run.py` | Runner: baseline arm, skill arm, judge, behavior checks, summary (the spec's `run.sh`; Python for reliable JSON parsing) |
| `evals/test_run.py` | Unit tests for the runner's pure functions |
| `evals/results/<run>/` | Raw outputs, verdicts, `results.json`, `summary.md` |
| `README.md`, `LICENSE`, `.gitignore` | Repo docs and hygiene |

---

### Task 1: Research the official guides

**Files:**
- Create: `docs/research-notes.md`

**Interfaces:**
- Produces: `docs/research-notes.md` with sections `## Sources` (one `### <Vendor> — <title>` per source, each with URL, fetch date, 5–10 key points), `## Synthesis` (numbered principles, each tagged with source names), `## Advice we deliberately avoid` (each item with the source evidence). Tasks 5, 6 and 8 cite this file.

- [ ] **Step 1: Fetch each source** (use the `web-fetch` agent; if a URL redirects or 404s, follow to the current official page and record the final URL):
  - Anthropic prompt engineering overview + Claude best-practices pages: `https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview` and the "Claude 4 / current models best practices" page linked from it
  - Anthropic: `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`
  - OpenAI: `https://platform.openai.com/docs/guides/prompt-engineering` and the GPT-5 prompting guide `https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide`
  - Google: `https://ai.google.dev/gemini-api/docs/prompting-strategies`
  - DAIR.AI: `https://www.promptingguide.ai/` (techniques index)

  Ask each fetch for: the concrete recommendations, anything the source says changed for current/reasoning models, and anything it warns against.

- [ ] **Step 2: Write `docs/research-notes.md`.** Paraphrase; quotes at most one sentence each. In `## Advice we deliberately avoid`, cover at minimum: forced manual chain-of-thought for reasoning models, blanket temperature rules, ALL-CAPS/aggressive emphasis, over-literal few-shot copying, one-size-fits-all mega-templates — each with what the sources actually say. If a source contradicts one of these, record that honestly and adjust.

- [ ] **Step 3: Verify** every source section has a URL that was actually fetched in Step 1 (no URLs from memory alone).

- [ ] **Step 4: Commit**
```bash
git add docs/research-notes.md
git commit -m "docs: add verified research notes from official prompting guides"
```

---

### Task 2: Eval harness

**Files:**
- Create: `evals/cases.json`, `evals/judge_prompt.md`, `evals/run.py`, `evals/test_run.py`, `.gitignore`

**Interfaces:**
- Produces (in `evals/run.py`):
  - `build_baseline_cmd(prompt: str, model: str | None = None) -> list[str]`
  - `build_skill_cmd(prompt: str, plugin_dir: str, model: str | None = None) -> list[str]`
  - `build_judge_cmd(judge_prompt: str, model: str | None = None) -> list[str]`
  - `render_judge_prompt(template: str, request: str, response_a: str, response_b: str) -> str`
  - `parse_verdict(text: str) -> dict` (keys `winner` ∈ {"A","B","tie"}, `reason`, `a_asks_before_answering: bool`, `b_asks_before_answering: bool`; raises `ValueError`)
  - `map_verdict(verdict: dict, skill_is_a: bool) -> tuple[str, bool]` → (`"skill"|"baseline"|"tie"`, skill_asked)
  - `behavior_failures(case: dict, skill_output: str, skill_asked: bool) -> list[str]`
  - `summarize(rows: list[dict]) -> dict` (keys `cases, skill, baseline, tie, win_rate, behavior_pass`)
  - `render_summary_md(summary: dict, rows: list[dict]) -> str`
  - CLI: `python3 evals/run.py [--cases id,id] [--model M] [--judge-model M] [--baseline-only] [--workers N] [--seed N] [--out DIR]`
  - Output dir files: `<id>.baseline.md`, `<id>.skill.md`, `<id>.verdict.json`, `results.json`, `summary.md`
- Case schema: `{"id": str, "category": str, "prompt": str, "expect": {"asks"?: bool, "max_chars"?: int}}`

- [ ] **Step 1: Write `evals/cases.json`**

```json
[
  {"id": "code-email-validate", "category": "code", "prompt": "write a function to validate emails in js", "expect": {"asks": false}},
  {"id": "code-slow-api", "category": "code", "prompt": "my node api is slow when i fetch users with their posts. how do i fix it", "expect": {"asks": false}},
  {"id": "code-pg-backup", "category": "code", "prompt": "bash script to backup my postgres db every night", "expect": {"asks": false}},
  {"id": "writing-linkedin-job", "category": "writing", "prompt": "write a linkedin post that i got a new job as backend developer", "expect": {"asks": false}},
  {"id": "writing-late-email", "category": "writing", "prompt": "email to client that the project will be 2 weeks late", "expect": {"asks": false}},
  {"id": "writing-readme", "category": "writing", "prompt": "write readme for my todo app made with react and firebase", "expect": {"asks": false}},
  {"id": "analysis-pg-vs-mongo", "category": "analysis", "prompt": "postgres or mongodb for my app?", "expect": {"asks": false}},
  {"id": "analysis-jwt", "category": "analysis", "prompt": "explain how jwt works", "expect": {"asks": false}},
  {"id": "creative-cab-names", "category": "creative", "prompt": "name ideas for my cab booking app", "expect": {"asks": false}},
  {"id": "creative-landing-copy", "category": "creative", "prompt": "landing page headline and copy for ai resume builder", "expect": {"asks": false}},
  {"id": "prompt-meeting-summary", "category": "prompt", "prompt": "write a prompt for chatgpt to summarize my meeting notes", "expect": {"asks": false}},
  {"id": "ambiguous-proposal", "category": "ambiguous", "prompt": "write a proposal", "expect": {"asks": true}},
  {"id": "trivial-percent", "category": "trivial", "prompt": "what is 15% of 240", "expect": {"asks": false, "max_chars": 300}}
]
```

- [ ] **Step 2: Write `evals/judge_prompt.md`**

````markdown
You are an exacting expert reviewer. Someone sent the REQUEST below to an AI assistant. Two different assistants answered. Decide which response better serves the person who sent the request.

Judge on these criteria, in order of importance:
1. Usefulness — how much closer the response gets the person to what they were actually trying to accomplish, including needs they implied but did not state.
2. Correctness — facts, code, numbers and claims are accurate; nothing is invented.
3. Specificity — concrete and tailored rather than generic boilerplate.
4. Fit — format, length, tone and depth suit the request. A short question deserves a short answer; padding, preamble and filler count against a response.
5. Judgment on ambiguity — if the request is too vague to act on without guessing wildly, a short, sharp clarifying question beats a confident answer to the wrong problem. If the request is actionable, asking instead of answering is worse.

Do not favor a response for being longer or for formatting alone.

<request>
{{REQUEST}}
</request>

<response_a>
{{RESPONSE_A}}
</response_a>

<response_b>
{{RESPONSE_B}}
</response_b>

Reply with only a JSON object and no other text:
{"reason": "<2-3 sentences>", "winner": "A" or "B" or "tie", "a_asks_before_answering": true if response A mainly asks clarifying questions instead of delivering a result else false, "b_asks_before_answering": same for response B}
````

- [ ] **Step 3: Write the failing tests `evals/test_run.py`**

```python
import unittest
import run


class CommandTests(unittest.TestCase):
    def test_baseline_cmd_is_isolated_and_has_no_plugin(self):
        cmd = run.build_baseline_cmd("hello")
        self.assertEqual(cmd[:4], ["claude", "-p", "--setting-sources", "project"])
        self.assertNotIn("--plugin-dir", cmd)
        self.assertEqual(cmd[-1], "hello")

    def test_skill_cmd_loads_plugin_and_prefixes_command(self):
        cmd = run.build_skill_cmd("hello", "/repo", model="opus")
        self.assertIn("--plugin-dir", cmd)
        self.assertEqual(cmd[cmd.index("--plugin-dir") + 1], "/repo")
        self.assertEqual(cmd[cmd.index("--model") + 1], "opus")
        self.assertEqual(cmd[-1], "/promptking hello")

    def test_judge_cmd_disables_skills(self):
        self.assertIn("--disable-slash-commands", run.build_judge_cmd("x"))


class JudgeTests(unittest.TestCase):
    def test_render_fills_all_slots(self):
        out = run.render_judge_prompt("{{REQUEST}}|{{RESPONSE_A}}|{{RESPONSE_B}}", "r", "a", "b")
        self.assertEqual(out, "r|a|b")

    def test_parse_verdict_extracts_json_from_noise(self):
        text = 'Sure:\n{"reason": "x", "winner": "B", "a_asks_before_answering": false, "b_asks_before_answering": true}\n'
        v = run.parse_verdict(text)
        self.assertEqual(v["winner"], "B")
        self.assertTrue(v["b_asks_before_answering"])

    def test_parse_verdict_rejects_bad_winner(self):
        with self.assertRaises(ValueError):
            run.parse_verdict('{"reason": "x", "winner": "C", "a_asks_before_answering": false, "b_asks_before_answering": false}')

    def test_parse_verdict_rejects_missing_json(self):
        with self.assertRaises(ValueError):
            run.parse_verdict("no json here")

    def test_map_verdict_when_skill_is_b(self):
        v = {"winner": "B", "a_asks_before_answering": False, "b_asks_before_answering": True}
        self.assertEqual(run.map_verdict(v, skill_is_a=False), ("skill", True))
        self.assertEqual(run.map_verdict(v, skill_is_a=True), ("baseline", False))

    def test_map_verdict_tie(self):
        v = {"winner": "tie", "a_asks_before_answering": False, "b_asks_before_answering": False}
        self.assertEqual(run.map_verdict(v, skill_is_a=True)[0], "tie")


class BehaviorTests(unittest.TestCase):
    def test_flags_asking_when_it_should_proceed(self):
        fails = run.behavior_failures({"expect": {"asks": False}}, "Which language?", True)
        self.assertEqual(fails, ["asked when it should have proceeded"])

    def test_flags_not_asking_when_it_should(self):
        fails = run.behavior_failures({"expect": {"asks": True}}, "Here is a proposal...", False)
        self.assertEqual(fails, ["should have asked first"])

    def test_flags_overlong_trivial_answer(self):
        fails = run.behavior_failures({"expect": {"max_chars": 10}}, "x" * 11, False)
        self.assertEqual(len(fails), 1)
        self.assertIn("too long", fails[0])

    def test_flags_leaked_brief(self):
        fails = run.behavior_failures({"expect": {}}, "Real goal: ship it", False)
        self.assertEqual(len(fails), 1)
        self.assertIn("leaked", fails[0])

    def test_clean_output_passes(self):
        self.assertEqual(run.behavior_failures({"expect": {"asks": False}}, "36", False), [])


class SummaryTests(unittest.TestCase):
    def test_win_rate_excludes_ties(self):
        rows = [
            {"winner": "skill", "behavior_failures": []},
            {"winner": "skill", "behavior_failures": ["x"]},
            {"winner": "baseline", "behavior_failures": []},
            {"winner": "tie", "behavior_failures": []},
        ]
        s = run.summarize(rows)
        self.assertEqual((s["cases"], s["skill"], s["baseline"], s["tie"]), (4, 2, 1, 1))
        self.assertAlmostEqual(s["win_rate"], 0.667, places=3)
        self.assertEqual(s["behavior_pass"], 3)

    def test_summary_md_has_table(self):
        rows = [{"id": "c1", "winner": "skill", "reason": "better", "behavior_failures": []}]
        md = run.render_summary_md(run.summarize(rows), rows)
        self.assertIn("| c1 | skill |", md)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `cd evals && python3 -m unittest test_run -v`
Expected: FAIL / ERROR with `ModuleNotFoundError: No module named 'run'`

- [ ] **Step 5: Write `evals/run.py`**

```python
#!/usr/bin/env python3
"""PromptKing eval runner.

For each case: run the rough prompt without the skill (baseline) and with
`/promptking` (skill) in fresh headless Claude Code sessions, then have a
blind judge compare the two in random A/B order.
"""
import argparse
import concurrent.futures as cf
import datetime
import json
import pathlib
import random
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
EVALS = ROOT / "evals"
LEAK_MARKERS = ["Real goal", "Expert lens", "Quality bar", "Decode →", "<brief>"]


def _base(model):
    cmd = ["claude", "-p", "--setting-sources", "project"]
    if model:
        cmd += ["--model", model]
    return cmd


def build_baseline_cmd(prompt, model=None):
    return _base(model) + [prompt]


def build_skill_cmd(prompt, plugin_dir, model=None):
    return _base(model) + ["--plugin-dir", str(plugin_dir), f"/promptking {prompt}"]


def build_judge_cmd(judge_prompt, model=None):
    return _base(model) + ["--disable-slash-commands", judge_prompt]


def render_judge_prompt(template, request, response_a, response_b):
    return (
        template.replace("{{REQUEST}}", request)
        .replace("{{RESPONSE_A}}", response_a)
        .replace("{{RESPONSE_B}}", response_b)
    )


def parse_verdict(text):
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object in judge output")
    data = json.loads(text[start : end + 1])
    if data.get("winner") not in ("A", "B", "tie"):
        raise ValueError(f"bad winner: {data.get('winner')!r}")
    for key in ("a_asks_before_answering", "b_asks_before_answering"):
        if not isinstance(data.get(key), bool):
            raise ValueError(f"missing boolean {key}")
    return data


def map_verdict(verdict, skill_is_a):
    w = verdict["winner"]
    if w == "tie":
        winner = "tie"
    else:
        winner = "skill" if (w == "A") == skill_is_a else "baseline"
    key = "a_asks_before_answering" if skill_is_a else "b_asks_before_answering"
    return winner, verdict[key]


def behavior_failures(case, skill_output, skill_asked):
    fails = []
    expect = case.get("expect", {})
    if "asks" in expect and expect["asks"] != skill_asked:
        fails.append("should have asked first" if expect["asks"] else "asked when it should have proceeded")
    if "max_chars" in expect and len(skill_output) > expect["max_chars"]:
        fails.append(f"too long for a trivial request ({len(skill_output)} > {expect['max_chars']} chars)")
    lowered = skill_output.lower()
    for marker in LEAK_MARKERS:
        if marker.lower() in lowered:
            fails.append(f"leaked internal brief marker: {marker!r}")
    return fails


def summarize(rows):
    counts = {"skill": 0, "baseline": 0, "tie": 0}
    for r in rows:
        counts[r["winner"]] += 1
    decided = counts["skill"] + counts["baseline"]
    return {
        "cases": len(rows),
        **counts,
        "win_rate": round(counts["skill"] / decided, 3) if decided else 0.0,
        "behavior_pass": sum(1 for r in rows if not r["behavior_failures"]),
    }


def render_summary_md(summary, rows):
    lines = [
        "# PromptKing eval summary",
        "",
        f"- Cases: {summary['cases']}",
        f"- Skill wins: {summary['skill']} · Baseline wins: {summary['baseline']} · Ties: {summary['tie']}",
        f"- Win rate (excluding ties): {summary['win_rate']:.0%}",
        f"- Behavior checks passed: {summary['behavior_pass']}/{summary['cases']}",
        "",
        "| Case | Winner | Judge reason | Behavior failures |",
        "|---|---|---|---|",
    ]
    for r in rows:
        reason = r.get("reason", "").replace("|", "/").replace("\n", " ")
        fails = "; ".join(r["behavior_failures"]) or "—"
        lines.append(f"| {r['id']} | {r['winner']} | {reason} | {fails} |")
    return "\n".join(lines) + "\n"


def run_claude(cmd, timeout=900):
    with tempfile.TemporaryDirectory() as cwd:
        proc = subprocess.run(
            cmd, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout
        )
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.strip()[:500]}")
    return proc.stdout.strip()


def run_case(case, index, args, template, out):
    cid = case["id"]
    baseline = run_claude(build_baseline_cmd(case["prompt"], args.model))
    (out / f"{cid}.baseline.md").write_text(baseline + "\n")
    if args.baseline_only:
        return None
    skill = run_claude(build_skill_cmd(case["prompt"], ROOT, args.model))
    (out / f"{cid}.skill.md").write_text(skill + "\n")

    skill_is_a = random.Random(args.seed * 1000 + index).random() < 0.5
    a, b = (skill, baseline) if skill_is_a else (baseline, skill)
    judge_text = run_claude(build_judge_cmd(render_judge_prompt(template, case["prompt"], a, b), args.judge_model))
    verdict = parse_verdict(judge_text)
    winner, skill_asked = map_verdict(verdict, skill_is_a)
    row = {
        "id": cid,
        "category": case["category"],
        "winner": winner,
        "reason": verdict["reason"],
        "skill_was": "A" if skill_is_a else "B",
        "skill_asked": skill_asked,
        "behavior_failures": behavior_failures(case, skill, skill_asked),
    }
    (out / f"{cid}.verdict.json").write_text(json.dumps({**row, "raw": verdict}, indent=2) + "\n")
    return row


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cases", help="comma-separated case ids (default: all)")
    p.add_argument("--model")
    p.add_argument("--judge-model")
    p.add_argument("--baseline-only", action="store_true")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--out")
    args = p.parse_args(argv)

    cases = json.loads((EVALS / "cases.json").read_text())
    if args.cases:
        wanted = set(args.cases.split(","))
        cases = [c for c in cases if c["id"] in wanted]
    template = (EVALS / "judge_prompt.md").read_text()
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = pathlib.Path(args.out) if args.out else EVALS / "results" / stamp
    out.mkdir(parents=True, exist_ok=True)

    rows, errors = [], []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_case, c, i, args, template, out): c["id"] for i, c in enumerate(cases)}
        for fut in cf.as_completed(futures):
            cid = futures[fut]
            try:
                row = fut.result()
                print(f"done  {cid}" + (f"  → {row['winner']}" if row else ""), flush=True)
                if row:
                    rows.append(row)
            except Exception as exc:  # report and keep going
                errors.append(f"{cid}: {exc}")
                print(f"ERROR {cid}: {exc}", file=sys.stderr, flush=True)

    if not args.baseline_only:
        rows.sort(key=lambda r: [c["id"] for c in cases].index(r["id"]))
        summary = summarize(rows)
        (out / "results.json").write_text(json.dumps({"summary": summary, "rows": rows, "errors": errors}, indent=2) + "\n")
        (out / "summary.md").write_text(render_summary_md(summary, rows))
        print(render_summary_md(summary, rows))
    print(f"outputs: {out}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd evals && python3 -m unittest test_run -v`
Expected: all 16 tests PASS

- [ ] **Step 7: Write `.gitignore`**

```
__pycache__/
*.pyc
.DS_Store
```

- [ ] **Step 8: Commit**
```bash
git add evals/cases.json evals/judge_prompt.md evals/run.py evals/test_run.py .gitignore
git commit -m "test: add baseline-vs-skill eval harness with blind judging"
```

---

### Task 3: Plugin scaffold and always-on hook

**Files:**
- Create: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `hooks/hooks.json`, `hooks/always-on.sh`, `tests/test_hook.sh`, `LICENSE`, `skills/promptking/SKILL.md` (temporary stub, replaced in Task 5)

**Interfaces:**
- Produces: plugin `promptking` loadable via `--plugin-dir <repo>`; hook prints the JSON below iff `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/promptking/always-on` exists. Task 5's toggle creates/removes exactly that path.

- [ ] **Step 1: Write the failing hook test `tests/test_hook.sh`**

```sh
#!/bin/sh
# Tests for hooks/always-on.sh. Run: sh tests/test_hook.sh
set -u
HOOK="$(cd "$(dirname "$0")/.." && pwd)/hooks/always-on.sh"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
fail=0

out=$(printf '{"prompt":"hi"}' | CLAUDE_CONFIG_DIR="$T" sh "$HOOK"); rc=$?
if [ "$rc" -eq 0 ] && [ -z "$out" ]; then echo "PASS flag absent -> silent"; else echo "FAIL flag absent (rc=$rc out=$out)"; fail=1; fi

mkdir -p "$T/promptking" && touch "$T/promptking/always-on"
out=$(printf '{"prompt":"hi"}' | CLAUDE_CONFIG_DIR="$T" sh "$HOOK"); rc=$?
if [ "$rc" -eq 0 ] && printf '%s' "$out" | python3 -c '
import json, sys
d = json.load(sys.stdin)["hookSpecificOutput"]
assert d["hookEventName"] == "UserPromptSubmit"
assert "promptking" in d["additionalContext"].lower()
'; then echo "PASS flag present -> context JSON"; else echo "FAIL flag present (rc=$rc out=$out)"; fail=1; fi

exit $fail
```

- [ ] **Step 2: Run it to verify it fails**

Run: `sh tests/test_hook.sh`
Expected: both FAIL (hook file missing), exit 1

- [ ] **Step 3: Write `hooks/always-on.sh`** (then `chmod +x hooks/always-on.sh`)

```sh
#!/bin/sh
# PromptKing always-on hook (UserPromptSubmit).
# Adds context only while the flag file exists. Fails open: never blocks a prompt.
cat >/dev/null 2>&1
FLAG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/promptking/always-on"
[ -f "$FLAG" ] || exit 0
printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"PromptKing always-on mode is enabled. Handle this message with the promptking skill (Decode, Brief, Execute, Verify, Deliver) unless it is a slash command, a short acknowledgement, or a direct answer to a question you just asked."}}'
exit 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `sh tests/test_hook.sh`
Expected: `PASS flag absent -> silent`, `PASS flag present -> context JSON`, exit 0

- [ ] **Step 5: Write `hooks/hooks.json`**

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          { "type": "command", "command": "sh \"${CLAUDE_PLUGIN_ROOT}/hooks/always-on.sh\"" }
        ]
      }
    ]
  }
}
```

- [ ] **Step 6: Write `.claude-plugin/plugin.json`**

```json
{
  "name": "promptking",
  "description": "Turns rough requests into expert-quality results: silently builds an expert brief, executes it, and delivers only the finished work.",
  "version": "1.0.0",
  "author": { "name": "Rafay Shaikh", "url": "https://github.com/rafay247" },
  "homepage": "https://github.com/rafay247/promptking",
  "repository": "https://github.com/rafay247/promptking",
  "license": "MIT",
  "keywords": ["prompt-engineering", "context-engineering", "skills", "productivity", "claude-code"]
}
```

- [ ] **Step 7: Write `.claude-plugin/marketplace.json`**

```json
{
  "name": "promptking",
  "description": "PromptKing marketplace",
  "owner": { "name": "Rafay Shaikh", "url": "https://github.com/rafay247" },
  "plugins": [
    {
      "name": "promptking",
      "description": "Turns rough requests into expert-quality results.",
      "version": "1.0.0",
      "source": "./",
      "author": { "name": "Rafay Shaikh", "url": "https://github.com/rafay247" }
    }
  ]
}
```

- [ ] **Step 8: Write stub `skills/promptking/SKILL.md`** (replaced in Task 5)

```markdown
---
name: promptking
description: Stub. Use when the user invokes promptking.
---
Reply with exactly: PROMPTKING-STUB
```

- [ ] **Step 9: Write `LICENSE`** — the standard MIT license text with `Copyright (c) 2026 Rafay Shaikh`.

- [ ] **Step 10: Verify the plugin loads and the hook reaches the model**

```bash
claude -p --setting-sources project --plugin-dir "$PWD" "/promptking hi" < /dev/null
```
Expected: `PROMPTKING-STUB`

```bash
mkdir -p ~/.claude/promptking && touch ~/.claude/promptking/always-on
claude -p --setting-sources project --plugin-dir "$PWD" "Answer yes or no only: did you receive any context mentioning PromptKing always-on mode?" < /dev/null
rm -f ~/.claude/promptking/always-on
```
Expected: `yes`, and the flag file is removed afterwards.

- [ ] **Step 11: Commit**
```bash
git add .claude-plugin hooks tests skills LICENSE
git commit -m "feat: add plugin scaffold and always-on hook"
```

---

### Task 4: Baseline observation (RED)

**Files:**
- Create: `docs/baseline-observations.md`, `evals/results/baseline/` (outputs)

**Interfaces:**
- Consumes: `evals/run.py --baseline-only` (Task 2)
- Produces: `docs/baseline-observations.md` — one `### <case id>` per case with 2–4 bullets naming concrete gaps an expert would fix. Tasks 5–6 design against these gaps.

- [ ] **Step 1: Run the baseline arm**

Run: `python3 evals/run.py --baseline-only --out evals/results/baseline`
Expected: 13 `done <id>` lines, 13 `*.baseline.md` files, exit 0

- [ ] **Step 2: Read every baseline output** and write `docs/baseline-observations.md`. For each case, name specific gaps (e.g. "email regex rejects valid `+` addresses, no tests, no note about server-side validation"; "LinkedIn post is generic, no hook line, no specifics placeholder"). End with `## Cross-cutting patterns`: the 3–6 recurring weaknesses.

- [ ] **Step 3: Commit**
```bash
git add docs/baseline-observations.md evals/results/baseline
git commit -m "docs: record baseline output gaps before writing the skill"
```

---

### Task 5: Core skill — SKILL.md and brief checklist (GREEN)

**REQUIRED SUB-SKILL:** follow superpowers:writing-skills for skill authoring conventions.

**Files:**
- Modify (replace stub): `skills/promptking/SKILL.md`
- Create: `skills/promptking/references/brief-checklist.md`

**Interfaces:**
- Consumes: flag path from Task 3; gaps from Task 4; principles from Task 1.
- Produces: routing table naming exactly these files (created in Task 6): `references/code.md`, `references/writing.md`, `references/analysis-research.md`, `references/creative-design.md`, `references/prompts-for-ai.md`.

- [ ] **Step 1: Write `skills/promptking/SKILL.md`** — this draft, adjusted only where Task 1/Task 4 findings call for it:

````markdown
---
name: promptking
description: Turns a rough request into an expert-quality result. Silently builds an expert brief from the request, executes it, and delivers only the finished work. Use when the user invokes /promptking with a request, when PromptKing always-on context is present, or when the user asks to turn PromptKing on or off.
argument-hint: "<rough request> | on | off"
---

# PromptKing

The user gave you a rough request. Deliver the result a top expert would produce if they had been handed a perfect brief. The brief stays in your head; the user sees only the finished work.

## Toggle: `on` / `off`

If the arguments are exactly `on` or `off`, handle the toggle and stop.

- `on`: run `mkdir -p "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/promptking" && touch "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/promptking/always-on"`, then reply `PromptKing always-on: enabled. Every message gets the PromptKing treatment until you run /promptking off.`
- `off`: run `rm -f "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/promptking/always-on"`, then reply `PromptKing always-on: disabled.`
- No shell available (for example on claude.ai): explain that always-on mode needs the Claude Code plugin, and that `/promptking <request>` works everywhere.

## Workflow

1. **Decode.** Separate what was literally typed from what the person is trying to get done. When the request concerns their project, read the relevant files or context instead of guessing.
2. **Brief.** Work through `references/brief-checklist.md` silently. Scale it to the request: a one-line factual question needs a moment of thought and a direct answer; a substantial deliverable gets the full checklist.
3. **Execute.** Produce the deliverable your brief describes. Load the matching domain reference below first.
4. **Verify.** Check the draft against your quality bar and pitfall list, and fix what fails. Re-check every fact, API, version, command and number you would be embarrassed to get wrong.
5. **Deliver.** Send the result, following the output rules.

## Ask or assume

Ask only when a wrong guess would make the whole result useless: there is no topic, the target is unknown, or two likely readings lead to completely different deliverables. Then ask at most two short questions, each with a suggested default answer, and stop. In every other case, proceed on the most sensible assumptions.

## Output rules

- Open with the deliverable itself. No preamble, no restating the request, no description of your process.
- Never show the brief, the checklist, or an "enhanced prompt". (Exception: when the deliverable *is* a prompt, the prompt is the result.)
- If you made an assumption that shapes the result and the user might want otherwise, end with one line: `Assumed: <assumption>; <assumption>.` Keep it under 25 words. Omit it when nothing meaningful was assumed.
- Make it as long as the need requires and no longer.

## Domain references

| The result is… | Load |
|---|---|
| code, scripts, debugging, architecture, DevOps | `references/code.md` |
| emails, posts, docs, READMEs, letters, any prose | `references/writing.md` |
| explanations, comparisons, decisions, research | `references/analysis-research.md` |
| names, ideas, marketing copy, visual or UI direction | `references/creative-design.md` |
| a prompt, system prompt, or agent instructions for an AI | `references/prompts-for-ai.md` |

For mixed requests, load each relevant file. If a reference file cannot be read, continue without it.
````

- [ ] **Step 2: Write `references/brief-checklist.md`** with a short intro ("work through silently; scale to the request") and one section per item, each giving 2–4 guiding questions and one short good-vs-weak example:
  1. Real goal — what the person will *do* with the result.
  2. Deliverable — form, length, format that best serve that goal.
  3. Expert lens — who the best practitioner is; what they would do that an average answer would not.
  4. Context — what the conversation, files, or repo already reveal.
  5. Quality bar — 3–5 concrete criteria an expert reviewer would judge by.
  6. Gaps — ask (only if a wrong guess wastes the work) or assume (record for the `Assumed:` line).
  7. Pitfalls — typical failure modes for this task type, drawing on `## Cross-cutting patterns` in `docs/baseline-observations.md`.

- [ ] **Step 3: Verify loading and toggle**

```bash
claude -p --setting-sources project --plugin-dir "$PWD" "/promptking what is 15% of 240" < /dev/null
```
Expected: a short answer containing `36`, no brief leaked.

```bash
claude -p --setting-sources project --plugin-dir "$PWD" --allowedTools "Bash(mkdir:*)" "Bash(touch:*)" "Bash(rm:*)" "/promptking on" < /dev/null; ls ~/.claude/promptking/always-on
claude -p --setting-sources project --plugin-dir "$PWD" --allowedTools "Bash(mkdir:*)" "Bash(touch:*)" "Bash(rm:*)" "/promptking off" < /dev/null; ls ~/.claude/promptking/always-on 2>&1
```
Expected: "enabled" reply and the file exists; then "disabled" reply and `No such file or directory`.

- [ ] **Step 4: Commit**
```bash
git add skills/promptking
git commit -m "feat: add PromptKing core skill and hidden brief checklist"
```

---

### Task 6: Domain reference files

**Files:**
- Create: `skills/promptking/references/code.md`, `writing.md`, `analysis-research.md`, `creative-design.md`, `prompts-for-ai.md`

**Interfaces:**
- Consumes: the routing table in `SKILL.md` (Task 5), `docs/research-notes.md`, `docs/baseline-observations.md`.

Each file uses the same structure, about 60–120 lines: `## What an expert result looks like`, `## Quality bar` (checklist), `## Pitfalls to avoid`, `## Calibrating depth` (when to go short vs long). Content must address the matching gaps in `docs/baseline-observations.md`.

- [ ] **Step 1: `code.md`** must cover: match the user's stack and versions (inspect the repo when available); working, complete code over fragments; edge cases and input validation; security defaults (no secrets in code, parameterized queries, least privilege); no invented APIs or flags; brief usage/run instructions; tests or a quick verification method when it matters; explain non-obvious decisions in one line each.
- [ ] **Step 2: `writing.md`** must cover: audience and channel conventions (email vs LinkedIn vs README); a strong first line; concrete specifics over generic claims, with clearly marked `[placeholders]` only for facts the writer must supply; tone matching the relationship; for bad news, own it, give the new date, the reason and the mitigation; cut filler and clichés; scannable structure for docs.
- [ ] **Step 3: `analysis-research.md`** must cover: lead with the answer or recommendation; make the decision criteria explicit; "it depends" only with the specific deciding factors; concrete examples and numbers; distinguish fact from judgment; flag uncertainty and dated information; layered explanations (core idea → mechanism → pitfalls) for "explain X".
- [ ] **Step 4: `creative-design.md`** must cover: a range of distinct directions rather than variations of one; rationale per option; practical constraints (domain/handle availability caveat, pronounceability, trademark caution) for names; for copy, the benefit-led headline, proof and CTA; a recommended pick.
- [ ] **Step 5: `prompts-for-ai.md`** must cover, each principle tagged to its source in `docs/research-notes.md`: clear role and goal; context and the reason behind constraints; delimiters/XML for separating data from instructions; explicit output format; examples used with care; escape hatch for missing information; positive framing; prompt chaining for multi-stage work; context-engineering basics (relevant context only, long documents first and the question last, note-taking/compaction for long agent runs); model-specific notes (reasoning models need less step-by-step scripting; avoid ALL-CAPS emphasis); deliver the prompt ready to paste with `{{variables}}` marked.
- [ ] **Step 6: Verify routing.** Run one case per domain through the skill and confirm each output reflects its reference (e.g. the code case includes run instructions and edge cases):

```bash
python3 evals/run.py --cases code-email-validate,writing-late-email,analysis-jwt,creative-cab-names,prompt-meeting-summary --out evals/results/smoke
```
Expected: 5 rows in `summary.md`, no ERROR lines.

- [ ] **Step 7: Commit**
```bash
git add skills/promptking/references
git commit -m "feat: add domain reference files for PromptKing"
```

---

### Task 7: Full eval and iteration (REFACTOR)

**Files:**
- Modify (as needed): `skills/promptking/SKILL.md`, `skills/promptking/references/*.md`
- Create: `evals/results/final/`

- [ ] **Step 1: Run the full eval**

Run: `python3 evals/run.py --out evals/results/round-1`
Expected: 13 rows, summary printed, exit 0.

- [ ] **Step 2: Diagnose.** For every baseline win, tie, or behavior failure, read both outputs and the judge's reason, and write a one-line root cause.

- [ ] **Step 3: Fix the skill**, targeting root causes rather than individual cases (no case-specific instructions in the skill). Re-run the affected cases plus three cases the skill already won, to catch regressions:

Run: `python3 evals/run.py --cases <affected>,<3 previous wins> --out evals/results/round-N`

- [ ] **Step 4: Repeat Steps 2–3 at most three rounds**, stopping early once the win rate is ≥ 75% and all behavior checks pass.

- [ ] **Step 5: Final full run** with a new seed:

Run: `python3 evals/run.py --seed 42 --out evals/results/final`
Record the numbers exactly as printed, whatever they are.

- [ ] **Step 6: Clean up.** Delete `evals/results/smoke` and `evals/results/round-*`; keep `baseline/` and `final/`.

- [ ] **Step 7: Commit**
```bash
git add -A skills evals/results
git commit -m "test: tune PromptKing against evals and record final results"
```

---

### Task 8: Professional README

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: `evals/results/final/summary.md`, `results.json`, raw outputs; `docs/research-notes.md`.

- [ ] **Step 1: Write `README.md`** with these sections, in order:
  1. Title `# 👑 PromptKing`, one-line tagline, badges: MIT license (shields.io), "Claude Code plugin".
  2. Two-sentence pitch: rough request in → expert-quality result out; you never have to see or write the "better prompt".
  3. **Before / after:** one real case from `evals/results/final/` (rough prompt, then trimmed excerpts of the baseline and PromptKing outputs, with the judge's reason). Label excerpts as trimmed.
  4. **How it works:** a Mermaid flowchart Decode → Brief → Execute → Verify → Deliver, then 3–4 sentences on the hidden brief and the ask-or-assume rule.
  5. **Install:** (a) plugin marketplace: `/plugin marketplace add rafay247/promptking` then `/plugin install promptking@promptking`; (b) manual: `git clone https://github.com/rafay247/promptking ~/.claude/plugins/promptking` and run `claude --plugin-dir ~/.claude/plugins/promptking`, or copy `skills/promptking` into `~/.claude/skills/` (skill only, no always-on); (c) claude.ai: zip the `skills/promptking` folder and upload it under Settings → Capabilities → Skills.
  6. **Usage:** `/promptking <request>` examples, `/promptking on|off`, what the `Assumed:` line means, and when it asks questions.
  7. **Benchmarks:** a table copied from the final `summary.md` (cases, wins/losses/ties, win rate, behavior checks), the method in 4 bullets, an honest note on sample size (n=13, single judge model), and a link to `evals/`. Include "Reproduce: `python3 evals/run.py`".
  8. **Design principles:** 5–6 bullets (result over prompt, scale to the task, ask only when it matters, verify before delivering, grounded in official guides).
  9. **Sources:** the URLs from `docs/research-notes.md`.
  10. **Project structure:** a short tree.
  11. **Contributing:** how to add an eval case and run the tests (`cd evals && python3 -m unittest test_run`, `sh tests/test_hook.sh`).
  12. **License:** MIT © 2026 Rafay Shaikh.

- [ ] **Step 2: Verify the README.** Every number matches `evals/results/final/summary.md`; every command was run in this plan or is a documented Claude Code command; no "100x" or other unmeasured claims; all links relative or to verified URLs. Validate the install path by actually installing from the local marketplace: `claude plugin marketplace add "$PWD"` then `claude plugin install promptking@promptking`; confirm `/promptking hi` works in a fresh `claude -p`, then `claude plugin uninstall promptking@promptking` and `claude plugin marketplace remove promptking`.

- [ ] **Step 3: Run all tests once more**

Run: `(cd evals && python3 -m unittest test_run) && sh tests/test_hook.sh`
Expected: all PASS.

- [ ] **Step 4: Commit**
```bash
git add README.md
git commit -m "docs: add README with install, usage and measured benchmarks"
```

---

### Task 9: Publish (only after Rafay approves)

- [ ] **Step 1: Ask Rafay for explicit approval to create the public repo and push.** Stop here until Rafay says yes.
- [ ] **Step 2:** Create `rafay247/promptking` (public, no auto-init) with the GitHub MCP `create_repository` tool, description: "Turn rough requests into expert-quality results — a Claude Code plugin."
- [ ] **Step 3:** `git remote add origin https://github.com/rafay247/promptking.git && git push -u origin main`
- [ ] **Step 4:** Verify with the GitHub MCP tools that the repo lists `README.md`, `.claude-plugin/`, `skills/`, and that the latest commit author is `Rafay Shaikh`.
