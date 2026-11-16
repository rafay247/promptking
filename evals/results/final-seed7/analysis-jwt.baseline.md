JWT (JSON Web Token) is a compact, self-contained way to represent claims (data) that can be verified and trusted because it's digitally signed. Here's how it works:

## Structure

A JWT is a single string with three parts separated by dots:
```
header.payload.signature
```

**1. Header** — metadata about the token, base64url-encoded JSON:
```json
{ "alg": "HS256", "typ": "JWT" }
```

**2. Payload** — the actual claims (data), base64url-encoded JSON:
```json
{ "sub": "user123", "name": "Alice", "role": "admin", "exp": 1732000000 }
```
Common claims: `sub` (subject/user ID), `exp` (expiration), `iat` (issued at), plus any custom data.

**3. Signature** — proves the token wasn't tampered with. Computed as:
```
HMACSHA256(base64url(header) + "." + base64url(payload), secret)
```
(or signed with a private key if using RSA/ECDSA — algorithms like RS256, ES256).

## The flow

1. **Login**: User sends credentials to the server.
2. **Issue**: Server verifies credentials, creates a JWT containing user claims, and signs it with a secret/private key.
3. **Store**: Client stores the token (e.g., in memory, localStorage, or a cookie).
4. **Use**: Client sends the JWT with each request, usually in the header:
   ```
   Authorization: Bearer <token>
   ```
5. **Verify**: Server recomputes the signature using its secret/public key and checks it matches. If valid and not expired, it trusts the claims inside — **without needing a database lookup**.

## Key properties

- **Stateless**: The server doesn't need to store session data — all the info is in the token itself. This makes JWTs great for scaling across multiple servers.
- **Signed, not encrypted**: By default, anyone can *read* the payload (it's just base64, not encryption) — don't put secrets in it. The signature only prevents *tampering*, it doesn't hide the content.
- **Verification is cheap**: Just a cryptographic check, no database round-trip (unlike opaque session tokens).

## Important caveats

- **Can't be revoked easily**: Since the server doesn't track active tokens, a stolen JWT remains valid until it expires. Mitigations: short expiration times + refresh tokens, or a server-side blocklist (which reintroduces state).
- **`exp` matters**: Always set and check expiration to limit damage from leaked tokens.
- **Algorithm confusion attacks**: Historically, some libraries let an attacker switch `alg` to `none` or trick RS256 verification into using HS256 with the public key as the secret. Always explicitly specify allowed algorithms when verifying.
- **Signature ≠ encryption**: If you need to hide the payload contents, use JWE (encrypted JWTs) instead of plain JWT/JWS.

**Typical use case**: Authentication/authorization in APIs and SPAs — login once, get a JWT, use it to prove identity on subsequent requests without re-sending credentials or requiring server-side session storage.
