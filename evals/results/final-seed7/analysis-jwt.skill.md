## How JWT (JSON Web Token) Works

A JWT is a self-contained, digitally-signed token that lets a server verify who a user is (and what they're allowed to do) without looking anything up in a database on every request.

**Structure**: three Base64URL-encoded parts joined by dots: `header.payload.signature`

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0IiwibmFtZSI6IkFsaSIsImV4cCI6MTczMTc2MDAwMH0.4f8h3k...
```

- **Header** — algorithm + token type: `{"alg": "HS256", "typ": "JWT"}`
- **Payload** — claims (data about the user/session): `{"sub": "1234", "name": "Ali", "exp": 1731760000}`. This is only encoded, not encrypted — anyone can read it.
- **Signature** — `HMACSHA256(base64(header) + "." + base64(payload), secret)` for symmetric signing, or an RSA/ECDSA private-key signature for asymmetric signing. This is what makes tampering detectable: change one character of the payload and the signature no longer matches.

**The flow**:
1. User logs in with credentials.
2. Server verifies them, builds a payload (user id, roles, expiry), signs it, sends the JWT back.
3. Client stores the token and sends it on each request, typically `Authorization: Bearer <token>`.
4. Server recomputes the signature with its secret/public key and compares it to the one in the token. If it matches and `exp` hasn't passed, the request is trusted — no database round-trip needed.
5. When the token expires, the client either re-authenticates or uses a separate longer-lived refresh token to get a new access token.

**Why it's useful**: stateless — any server instance holding the secret/public key can verify the token, which is why JWTs fit horizontally-scaled or microservice setups where you don't want a shared session store.

**Practical pitfalls to actually watch for:**
- **Never trust `alg` from the token.** Pin the expected algorithm server-side. The classic exploit is sending `"alg": "none"` or swapping RS256→HS256 and signing with the public key as if it were an HMAC secret — libraries that blindly honor the header's `alg` get fooled.
- **Storage**: don't put JWTs in `localStorage` if you can avoid it (XSS can read it). Prefer an `httpOnly`, `Secure`, `SameSite=Strict/Lax` cookie.
- **Expiry and rotation**: keep access tokens short-lived (minutes), use a refresh token (longer-lived, stored more carefully, revocable) to mint new ones. There's no built-in revocation — once issued, a JWT is valid until `exp` unless you maintain a blocklist or short expiries.
- **Validate everything**: signature, `exp`, `nbf`, `iss`, `aud` — not just "does it parse."
- **Don't put secrets in the payload** — it's base64, not encryption; anyone can decode and read it.

Assumed: you wanted the general web-auth mechanics (access + refresh token pattern), not a specific framework's implementation.
