No project files here, so I'll answer generically — this is almost certainly the classic **N+1 query problem**.

## Most likely cause

If you're doing something like:

```js
const users = await User.findAll();
for (const user of users) {
  user.posts = await Post.findAll({ where: { userId: user.id } });
}
```

You're firing 1 query for users + N queries (one per user) for posts. 100 users = 101 queries.

## Fix: eager load / join instead

**Sequelize**
```js
const users = await User.findAll({
  include: [{ model: Post }]
});
```

**Prisma**
```js
const users = await prisma.user.findMany({
  include: { posts: true }
});
```

**Mongoose**
```js
const users = await User.find().populate('posts');
```

**Raw SQL** — one query with a JOIN, then group rows in app code:
```sql
SELECT u.*, p.* FROM users u
LEFT JOIN posts p ON p.user_id = u.id;
```

## Other things to check if that's not it

1. **Missing index** on `posts.user_id` (and `users.id` if not PK) — run `EXPLAIN` on the query.
2. **Pagination** — don't fetch all users/posts at once; add `LIMIT`/`OFFSET` or cursor pagination.
3. **Over-fetching columns** — `SELECT *` on large text/blob columns (post bodies) when you only need a preview.
4. **No connection pooling** — check your DB client is reusing connections, not opening one per request.
5. **Serialization cost** — if posts are huge, JSON-stringifying thousands of nested objects is itself slow.

If you share the actual query/ORM code and which database you're using, I can point at the exact fix instead of guessing.
