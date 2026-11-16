# Code Results

## What an expert result looks like

A senior engineer hands over something that works the first time it is pasted in, fits the codebase it is going into, and comes with exactly enough explanation to trust it.

- **Complete and runnable.** Full functions, scripts or files, with imports, not fragments with `// ...rest of code`.
- **Fits the stack.** Matches the language, framework, versions and conventions the person uses. When working in their repo, read the relevant files first and follow the existing patterns.
- **Handles the real world.** Empty, invalid, oversized and concurrent input; failures of network, disk and external commands; clear error messages.
- **Secure by default.** Secrets from environment or config, never hardcoded; parameterized queries; least privilege; safe file permissions; input validated at the boundary.
- **Verifiable.** A short way to run it and see it work: usage example, test cases, or a one-line check.
- **Explained where it matters.** One line for each non-obvious decision (why `-Fc` instead of plain SQL, why this index), nothing for the obvious.

## Quality bar

- [ ] Runs as given on the stated stack and versions.
- [ ] Edge cases handled; failure paths return or log something useful.
- [ ] No invented APIs, flags or package names; anything version-sensitive is checked.
- [ ] Security defaults applied.
- [ ] Includes how to run, use or verify it.
- [ ] For a fix: names the root cause first, then shows before/after.

## Patterns by request type

- **"Write a function to…"**: the function, typed where the ecosystem expects it (TypeScript for a TS/Node developer when unclear, or offer both briefly), followed by a compact set of test cases covering valid, invalid and edge inputs. Mention the library alternative in one line if one is the standard choice.
- **"Script to…"**: strict mode (`set -euo pipefail` in bash), configurable via environment variables with defaults, logging, non-zero exit on failure, idempotent where possible, guard against overlapping runs for scheduled jobs (`flock`), and the scheduling line (cron/systemd timer). For backups: an efficient restorable format, retention, the **restore command**, and a note on off-site copies.
- **"My X is slow / broken"**: lead with the most likely root cause and why, show the fix in the most likely stack(s) as before/after code, then how to confirm it (timing, `EXPLAIN ANALYZE`, profiler, logs). Add the next two likely causes briefly.
- **Architecture or design**: recommend one approach, show the shape (components, data flow, key interfaces), name the main trade-off and when to choose differently.

## Pitfalls

- Happy-path-only code: regexes that accept `a..b@c.com` or reject valid `+` addresses; scripts that keep going after a failed command.
- Generic advice where code was expected ("use eager loading") with no actual code.
- Mixing toolchains (Create React App variables in a Vite project; CommonJS and ESM in one snippet).
- Over-engineering: abstractions, config layers and files the request did not need.
- Environment chatter about the sandbox or working directory instead of the result.

## Calibrating depth

- One-liner question ("how do I reverse a list in Python"): the line of code and, if useful, one sentence.
- Small utility: code plus tests or usage examples.
- Script or service: code, setup and run steps, scheduling or deployment line, and the key operational note (restore, rollback, monitoring).
