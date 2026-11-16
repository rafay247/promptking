The slow path is almost certainly the **N+1 query problem**: you fetch all users, then loop over them making a separate database call per user to get their posts — so 100 users means 101 round-trips instead of 1–2.

**How to confirm it fast:** turn on query logging and count queries for one request.
- Sequelize: `new Sequelize(url, { logging: console.log })`
- Mongoose: `mongoose.set('debug', true)`
- Raw SQL: wrap the handler in `console.time('fetchUsers')` / `console.timeEnd(...)` and check how many statements run per request.

If you see N+1 queries where you expected 1, that's the bug. Fix below for the two most common stacks — use whichever matches yours.

**Sequelize (SQL/Postgres/MySQL)**

```js
// Before — N+1: one query for users, then one SELECT per user for posts
const users = await User.findAll();
for (const user of users) {
  user.dataValues.posts = await Post.findAll({ where: { userId: user.id } });
}

// After — single query with a JOIN via eager loading
const users = await User.findAll({
  include: [{ model: Post, as: 'posts' }],
});
```

**Mongoose (MongoDB)**

```js
// Before — N+1: one find() for users, then one find() per user for posts
const users = await User.find();
for (const user of users) {
  user.posts = await Post.find({ userId: user._id });
}

// After — single round trip using populate (requires a `posts` virtual
// or a `postIds` ref field on User; or reference `userId` on Post with a virtual populate)
const users = await User.find().populate('posts');
```

If you're on Prisma instead, the equivalent fix is `prisma.user.findMany({ include: { posts: true } })`.

**If query count is already fine (1–2 queries) but it's still slow, check these next, in order:**
1. **Missing index** on the foreign key (`posts.userId`/`posts.user_id`). Run `EXPLAIN ANALYZE` on the join query — a sequential scan on `posts` means add `CREATE INDEX ON posts(user_id);` (or `PostSchema.index({ userId: 1 })` in Mongoose).
2. **No pagination/limit** — if you're returning every user and every post in one response, add `limit`/`offset` (or cursor pagination) so payload size doesn't grow unbounded as data grows.

Assumed: you're on Sequelize or Mongoose since those are the most common Node+SQL/Mongo pairings; swap in your actual ORM's eager-load syntax if different.
