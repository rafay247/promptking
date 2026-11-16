PostgreSQL — for a typical app, pick Postgres by default.

**Choose MongoDB if:**
- Your data is genuinely document-shaped and doesn't need cross-entity joins (e.g., storing heterogeneous JSON blobs, logs, event streams, CMS content with varying schemas per item).
- Schema will change frequently and unpredictably during early product exploration, and you don't want migrations in the loop yet.
- You need horizontal write scaling across many nodes from day one (rare for most apps before significant traffic).

**Choose Postgres if (the common case):**
- You have users, accounts, orders, relationships between entities — anything that benefits from joins and foreign keys.
- You need transactional integrity (money, inventory, bookings) — Postgres's ACID guarantees are stronger and more battle-tested.
- You want the data layer to double as application logic (constraints, triggers, generated columns) instead of enforcing everything in app code.
- You might need full-text search, JSON storage, geospatial data, or vector search (pgvector) later — Postgres does all of these natively via extensions, so you're not locked out of "document-style" flexibility by choosing it.

**The most common mistake**: picking MongoDB because "it's easier to get started" or "my data is JSON," then hitting a wall 6–12 months in when you need joins, transactions, or reporting — and migrating to Postgres under pressure. Postgres's `jsonb` column type already gives you schema-flexible JSON storage with indexing, so "my data is JSON-ish" isn't actually a reason to leave Postgres.

Practically: start with Postgres unless you can name a specific document-modeling or scaling requirement MongoDB solves that Postgres can't.

Assumed: "my app" is a typical CRUD/SaaS-style application with users and relational data, not a specialized logging/CMS/high-write-throughput system; no project files were found to indicate otherwise.
