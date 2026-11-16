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
        order = [c["id"] for c in cases]
        rows.sort(key=lambda r: order.index(r["id"]))
        summary = summarize(rows)
        (out / "results.json").write_text(json.dumps({"summary": summary, "rows": rows, "errors": errors}, indent=2) + "\n")
        (out / "summary.md").write_text(render_summary_md(summary, rows))
        print(render_summary_md(summary, rows))
    print(f"outputs: {out}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
