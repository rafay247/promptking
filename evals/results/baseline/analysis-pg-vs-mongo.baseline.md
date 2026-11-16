Depends on your data shape: if your data is relational (users, orders, foreign keys, things you'll query/join in flexible ways) go Postgres — it also now handles JSON/document data well via `jsonb`, so it covers most "maybe I need flexibility" cases too. MongoDB mainly wins when your data is naturally schema-less/nested documents with no real relations and you need horizontal write scaling from day one.

What's the app and data model look like? That'll make the call obvious.
