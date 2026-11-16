Empty directory, so this is a general question rather than one tied to existing code. It depends on your data:

- **Postgres** if your data has clear relationships (users, orders, payments), you need transactions/data integrity, or you'll want complex queries/joins and reporting later.
- **MongoDB** if your data is document-shaped and varies a lot in structure (e.g., flexible user-generated content, event logs), and you mostly fetch/write whole documents without many joins.

For most new apps I'd default to **Postgres** — it handles both relational and document-ish data well (via `jsonb`), has stronger consistency guarantees, and you're less likely to regret it as requirements grow. MongoDB mainly wins when your access patterns are truly document-centric and schema flexibility is a core need, not just a convenience.

What's the app, and what does the data look like? That'll make the call clearer.
