# How JWT Works

JWT (JSON Web Token) is a compact, self-contained way to represent identity/claims that can be verified without a database lookup.

## Structure

A JWT is three Base64URL-encoded parts separated by dots:

```
header.payload.signature
```

**1. Header** — metadata about the token:
```json
{ "alg": "HS256", "typ": "JWT" }
```

**2. Payload** — the claims (data):
```json
{ "sub": "user123", "role": "admin", "exp": 1732000000 }
```

**3. Signature** — cryptographic proof the token wasn't tampered with:
```
HMACSHA256(base64(header) + "." + base64(payload), secretKey)
```

## The flow

1. **Login**: User sends credentials to the server.
2. **Issue**: Server verifies credentials, creates a JWT, signs it with a secret (HMAC) or private key (RSA/ECDSA), and sends it to the client.
3. **Store**: Client stores the token (localStorage, cookie, memory, etc.) and sends it with subsequent requests — usually as `Authorization: Bearer <token>`.
4. **Verify**: Server receives the request, recomputes the signature over the header+payload using its secret/public key, and checks it matches. If it matches, the claims are trusted as untampered.
5. **No DB hit needed**: Because the signature proves integrity, the server doesn't need to look up a session in a database — it just trusts the claims (e.g., user ID, role, expiry).

## Key properties

- **Not encrypted by default** — payload is just Base64URL, anyone can decode and read it (don't put secrets in it). Signing proves *integrity*, not *confidentiality*. Use JWE if you need encryption.
- **Stateless** — the server doesn't store session state; the token itself carries everything needed.
- **Expiry via `exp` claim** — tokens are typically short-lived; revocation before expiry requires extra mechanisms (blocklists, short TTL + refresh tokens) since there's no server-side session to delete.
- **Signature algorithms**: symmetric (HS256 — same secret signs and verifies) or asymmetric (RS256/ES256 — private key signs, public key verifies, useful when multiple services need to verify but shouldn't be able to issue tokens).

## Common pitfalls (worth knowing)

- **`alg: none` / algorithm confusion attacks** — some old libraries let an attacker set `alg: none` or swap RS256 for HS256 using the public key as the HMAC secret. Always pin the expected algorithm server-side.
- **No revocation** — stolen tokens remain valid until expiry unless you maintain a blocklist.
- **Storing sensitive data in payload** — since it's readable by anyone with the token.

Want a code example of signing/verifying a JWT in a specific language?
