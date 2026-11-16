JWT (JSON Web Token) is a compact, self-contained way to pass verified claims between two parties — typically "this user is authenticated as X, with these permissions, until this time" — without the receiving server needing to look anything up in a database.

**Structure**: a JWT is three base64url-encoded parts joined by dots: `header.payload.signature`.

- **Header** — declares the algorithm and token type, e.g. `{"alg":"HS256","typ":"JWT"}`.
- **Payload** — the claims (data), e.g. `{"sub":"user123","role":"admin","iat":1700000000,"exp":1700003600}`. This is only encoded, not encrypted — anyone can decode and read it.
- **Signature** — `HMACSHA256(base64url(header) + "." + base64url(payload), secret)` for symmetric signing, or a private-key signature for RSA/ECDSA. This is what makes the token tamper-proof: change one character of the payload and the signature no longer matches.

**Flow**:
1. User logs in with credentials.
2. Server verifies them, builds a JWT with claims + expiry, signs it with a secret/private key, returns it.
3. Client stores the token and sends it on each request, usually as `Authorization: Bearer <token>`.
4. Server recomputes the signature using its secret/public key and checks it matches, checks `exp` hasn't passed, then trusts the claims — no DB lookup needed. That statelessness is the whole point of JWT over server-side sessions.

**Example** — a decoded payload might look like:
```json
{ "sub": "user123", "role": "admin", "iat": 1700000000, "exp": 1700003600 }
```
If someone edits `"role":"admin"` after the fact, the signature check on verify will fail and the server rejects the token.

**Practitioner pitfalls to avoid**:
- **Algorithm confusion attack**: never accept `alg` from the token blindly — pin the expected algorithm server-side (don't let an attacker switch `RS256` to `HS256` or `none`).
- **Storage**: don't put JWTs in `localStorage` for web apps if you can avoid it (XSS can steal them); prefer an `httpOnly`, `Secure`, `SameSite` cookie.
- **No server-side revocation**: a stateless JWT can't be invalidated before `exp` without extra infrastructure (a blocklist or short expiry + refresh tokens). Keep access-token `exp` short (minutes), issue a separate longer-lived refresh token to mint new ones.
- **Don't put secrets in the payload** — it's base64, not encryption; anyone can read it.
- **Validate everything on verify**: signature, `exp`, `iss`/`aud` if used — not just "it decoded successfully."

Assumed: generic web-auth context (not a specific framework/language); mention RS256 vs HS256 tradeoff only briefly since it wasn't asked for implementation code.
