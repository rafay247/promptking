Your API is almost certainly doing an **N+1 query problem**: one query to fetch users, then a separate query per user to fetch their posts (either explicit `for` loop + `await`, or a lazy-loaded ORM association). For 100 users that's 101 round-trips to the DB instead of 1-2.

**Before (N+1) — Sequelize example:**
```js
const users = await User.findAll();
for (const user of users) {
  user.dataValues.posts = await Post.findAll({ where: { userId: user.id } });
}
```

**After — eager load in one query:**
```js
const users = await User.findAll({
  include: [{ model: Post, as: 'posts' }],
});
```

**Same fix in Prisma:**
```js
const users = await prisma.user.findMany({
  include: { posts: true },
});
```

**Same fix in raw SQL (if you're not using an ORM):**
```js
const { rows } = await pool.query(`
  SELECT u.id, u.name, u.email,
         p.id AS post_id, p.title, p.body
  FROM users u
  LEFT JOIN posts p ON p.user_id = u.id
`);
// then group rows by u.id in JS into { ...user, posts: [...] }
```

**How to confirm it's actually N+1** before you ship the fix:
- Turn on query logging (`logging: console.log` in Sequelize, `log: ['query']` in Prisma, or `pg`'s query event) and count queries for one request — if it's `1 + N` instead of `1`, this is it.
- Or just wrap the handler in `console.time`/`console.timeEnd` and watch it drop from e.g. 800ms → 15ms after the fix.

**If that's not it, check these next (common #2 and #3 causes):**
1. **Missing index** on `posts.user_id` — even a single JOIN query is slow if Postgres/MySQL is doing a full table scan on posts. Run `EXPLAIN ANALYZE` on the JOIN query; if you see `Seq Scan` on posts, add `CREATE INDEX idx_posts_user_id ON posts(user_id);`.
2. **No pagination/limit** — if you're returning *all* users and *all* their posts in one payload, add `LIMIT`/`OFFSET` (or cursor pagination) rather than loading everything every request.

Assumed: you're using Node + Express with either Sequelize, Prisma, or raw `pg`/`mysql2`, and users→posts is a standard one-to-many on `posts.user_id`. If your stack differs (Mongoose, TypeORM, GraphQL resolvers), the root cause is the same but the fix syntax changes — tell me which and I'll give you the exact snippet.
