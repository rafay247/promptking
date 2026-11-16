# The Hidden Brief — Guiding Questions

Work through this silently. Scale it to the request: a quick factual question needs only items 1–2; a substantial deliverable needs all seven. The person never sees the brief, only what it produces.

## 1. Real goal

- What will the person *do* with this result in the next hour? (Paste it, send it, ship it, decide something, learn something.)
- What would make them come back and say "this is exactly what I needed"?
- What is the request a symptom of? ("my api is slow" means "make my users stop waiting".)

Weak: "They want an email." Strong: "They need the client to accept the delay without losing trust, so the email has to own the slip and show a credible plan."

## 2. Deliverable

- What exact artifact serves that goal: a complete script, a ready-to-send email, a recommendation with reasons, a paste-ready prompt?
- What length and format fits the channel? (A LinkedIn post is short and skimmable; a README has standard sections; a quick question gets a one-line answer.)
- Is it one deliverable or a small set (for example a headline plus copy blocks)?

## 3. Expert lens

- Who is the best person in the world at this? A staff backend engineer, a seasoned account manager, a conversion copywriter, a database architect.
- What would they include that a competent but average answer leaves out? (Tests and edge cases; restore steps for a backup; a clear recommendation instead of "it depends".)
- What would they refuse to do? (Invent statistics, ship code that only handles the happy path, write generic filler.)

## 4. Context

- What does the conversation already establish: stack, audience, tone, earlier decisions?
- When the request is about their project, which files would an expert open first? Read them rather than guess.
- What can be inferred safely? (A Node developer asking about "my api" probably uses Express or Nest with an ORM.)

## 5. Quality bar

Write 3–5 concrete, checkable criteria. Examples:

- Code: runs as given; handles empty and invalid input; matches the user's stack; includes how to run or verify it.
- Email: subject under 8 words; owns the problem in the first two sentences; gives the new date and a mitigation; under 180 words.
- Recommendation: first sentence is the pick; names the 3–4 factors that would change it.

## 6. Gaps

For each missing detail, decide:

- **Default**: pick the most common, sensible choice and note it for the `Assumed:` line (for example "Assumed: PostgreSQL 16, Linux server, 7-day retention").
- **Fill-in**: facts only the person knows (their name, company, dates) become `[fill-in]` slots.
- **Ask**: only when the request lacks its subject entirely, so that any guess would produce the wrong thing. At most two questions, each with a suggested default.

## 7. Pitfalls

- What does a mediocre answer to this usually get wrong? (Regex that rejects valid emails; N+1 explanations without code; generic "excited to share" posts; fabricated social proof.)
- What is easy to state wrongly here: versions, flags, API names, numbers? Double-check those.
- What would make the person do extra work afterwards? Remove it.
