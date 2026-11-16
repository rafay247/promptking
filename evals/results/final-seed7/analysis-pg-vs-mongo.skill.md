For a typical app, go with **PostgreSQL** by default — relational integrity, mature tooling, and flexibility to handle unstructured data (via `JSONB`) usually outweigh what MongoDB offers, unless your data is genuinely document-shaped from day one.

**Choose PostgreSQL if:**
- Your data has clear relationships (users → orders → items) that benefit from foreign keys and joins
- You need transactions across multiple records (payments, inventory, bookings)
- You want strong consistency and ACID guarantees by default
- You're not sure yet — Postgres's `JSONB` columns let you store flexible/schema-less data without giving up SQL, so you get both worlds

**Choose MongoDB if:**
- Your core data is naturally document-shaped and rarely needs cross-document joins (e.g., content/CMS blobs, event logs, product catalogs with wildly varying attributes per item)
- You expect very high write throughput with loose consistency requirements (analytics ingestion, telemetry)
- Your schema will change shape frequently and unpredictably, and enforcing a schema upfront would slow you down

**Most common mistake:** picking MongoDB early because "the schema might change," then bolting on relationships (users referencing orders referencing products) with manual joins in application code — reinventing what a relational database already does well, while losing transactional safety. Teams that do this often migrate back to Postgres within a year.

**Practical middle ground:** start on Postgres, use `JSONB` for the genuinely flexible parts of your schema. You get relational guarantees where they matter and document flexibility where you need it, without committing to two paradigms.

Assumed: "typical app" means a product with users, relationships between entities, and a need for data consistency (e.g., SaaS, e-commerce, social) rather than a pure logging/analytics/content-blob workload.
