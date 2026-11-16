Depends on your data shape: if your data is relational (users, orders, foreign keys, need transactions/joins, strong consistency) go Postgres; if it's document-like/schema-flexible (varying JSON shapes, high write throughput, no complex relations) MongoDB fits better. Postgres is also a safer default these days since it handles JSON well too (via `jsonb`) and gives you strong consistency if you change your mind later.

What's the app — what kind of data are you storing and what's the main access pattern (lots of joins/reports, or mostly simple reads/writes per document)?
