# Baseline Observations (no skill)

Run: `evals/results/baseline/` (Claude Code 2.1.220, headless, empty working directory, file-writing tools blocked). These are the gaps PromptKing has to close. Note that the baseline is already competent. The skill has to beat a strong default, not a weak one.

### ambiguous-proposal
- Correctly asks instead of guessing, but asks **four** questions with no suggested defaults, and offers a "polished artifact" option unrelated to the request.
- Expert version: one or two sharp questions, each with a sensible default, so the person can answer in seconds.

### analysis-jwt
- Solid and accurate: structure, flow, statelessness, `alg: none`, revocation.
- Gaps: no mention of where to store tokens safely (httpOnly cookie vs localStorage and the XSS/CSRF trade-off), refresh-token rotation, or `aud`/`iss` validation. Ends with a "Want a code example?" offer instead of just including a short one.

### analysis-pg-vs-mongo
- Two sentences, then defers: "What's the app and data model look like?"
- Expert version: commit to a default recommendation (Postgres for most apps), give the 3–4 deciding factors that would flip it, and say so in the `Assumed:` line.

### code-email-validate
- Works for the common case and sensibly recommends a library and confirmation emails.
- Gaps: accepts `a@b.c`, `a..b@c.com` and `.a@b.com`; no length limits (254/64); no tests; no note on Unicode/IDN; no TypeScript option for a Node/TS developer.

### code-pg-backup
- (First run stalled on a file-write permission prompt and returned no script at all. Fixed in the harness by blocking file-writing tools.)
- Re-run: decent script with retention, logging, `.pgpass` and cron.
- Gaps: plain-text `pg_dump` instead of `-Fc` custom format (no parallel or selective restore); no restore instructions or restore test; no lock against overlapping runs (`flock`); no off-site copy; the closing "saved at /tmp/... scratchpad" is environment noise.

### code-slow-api
- Lists the right causes (N+1, missing index, over-fetching, pagination) but stays generic and ends asking for code.
- Expert version: lead with the likely culprit (N+1), show the before/after fix in the most likely stacks (Prisma, Sequelize, Mongoose, raw SQL), the index to add, and how to confirm it with timing or `EXPLAIN`.

### creative-cab-names
- About 30 names in vibe groups, little rationale, some weak fits ("Flinch" for a ride app, "Trove").
- Expert version: fewer, stronger names across distinct strategies, with a one-line rationale each, a recommended shortlist, and a practical note on checking domain, app-store and trademark availability.

### creative-landing-copy
- Strongest baseline: full hero, value props, how-it-works and CTAs.
- Gaps: **invents a statistic** ("75% of resumes never reach a human") and a fake social-proof line naming Google, Amazon and Deloitte. It flags only one of them as a placeholder. Five headline options with no recommendation.

### prompt-meeting-summary
- Usable but thin: no role, no audience, no handling of long or messy notes, no "if missing, say so" for owners and dates, no output length guidance, no example of the format.
- Expert version: a ready-to-paste prompt with clear sections, a fallback for missing information, and a fill-in variable.

### trivial-percent
- `15% of 240 = **36**`. Ideal. PromptKing must not make this worse.

### writing-late-email
- Reasonable structure, but generic and heavy on placeholders. Weak on ownership ("we've run into…"), gives no mitigation plan or interim deliverable, and adds environment noise ("I don't have an email-sending tool").
- Expert version: take responsibility, give the new date, what's done, what's left, a concrete mitigation, and an offer to talk, with a short subject line and a few clearly marked fill-ins.

### writing-linkedin-job
- Generic template ("excited to share… next chapter 🚀"); no hook, no specifics, no story; hashtags tacked on.
- Expert version: a strong first line, one concrete detail (what you'll build or learn, who helped), a natural tone, a short length and clearly marked fill-ins for the company and stack.

### writing-readme
- On re-run it **asked five questions instead of delivering**, even though a solid README for "React + Firebase todo app" is entirely doable. (The first run delivered a generic README, mixing CRA and Vite environment variables.)
- Expert version: deliver a complete README on sensible assumptions (Vite + Firestore + Auth), with marked fill-ins, and list the assumptions in one line.

## Cross-cutting patterns

1. **Defers instead of delivering.** Asks for details or offers "Want me to…?" when a strong default answer was possible (pg-vs-mongo, slow-api, readme re-run, several closing offers).
2. **Generic over specific.** Template language and placeholder-heavy drafts where an expert would commit to concrete, plausible content (LinkedIn, late email).
3. **Missing the expert layer.** Correct but without the things a senior practitioner adds: edge cases and tests (email), restore and locking (backup), storage and security trade-offs (JWT), a recommendation (copy, names).
4. **Invented facts.** Fabricated statistics and social proof presented as copy.
5. **Over-asking when ambiguous.** Too many questions, with no defaults.
6. **Environment noise.** Remarks about empty directories, missing tools and sandbox paths that the person doesn't need.
