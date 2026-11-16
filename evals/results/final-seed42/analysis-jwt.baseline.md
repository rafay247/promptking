## How JWT (JSON Web Token) Works

A JWT is a compact, self-contained way to transmit information between parties as a digitally signed token — commonly used for authentication/authorization.

### Structure

A JWT is three Base64URL-encoded parts separated by dots:

```
header.payload.signature
```

**1. Header** — metadata about the token
```json
{ "alg": "HS256", "typ": "JWT" }
```

**2. Payload** — the actual data ("claims")
```json
{ "sub": "user123", "role": "admin", "exp": 1732000000 }
```
Common claims: `sub` (subject), `iat` (issued at), `exp` (expiration), plus any custom data.

**3. Signature** — proof the token wasn't tampered with
```
HMACSHA256(base64(header) + "." + base64(payload), secretKey)
```

### The Flow

1. **Login**: User submits credentials to the server.
2. **Issue token**: Server verifies credentials, creates a JWT, signs it with a secret key, sends it back to the client.
3. **Store token**: Client stores it (localStorage, cookie, etc.).
4. **Use token**: Client sends the JWT with each request, usually in the header:
   ```
   Authorization: Bearer <token>
   ```
5. **Verify**: Server checks the signature using the secret (or public key) to confirm the token is valid and unmodified, then reads the claims to authorize the request — **without needing a database lookup or session store**.

### Key Properties

- **Stateless**: The server doesn't need to store session data — all necessary info is in the token itself.
- **Signed, not encrypted** (by default): The payload is just Base64-encoded, not hidden. Anyone can decode and read it — don't put secrets in it. The signature only guarantees *integrity* (it hasn't been altered), not confidentiality.
- **Algorithms**: 
  - Symmetric (HS256): same secret key signs and verifies — used when one party issues and verifies.
  - Asymmetric (RS256/ES256): private key signs, public key verifies — useful when multiple services need to verify tokens without holding the signing secret.
- **Expiration**: `exp` claim limits how long a token is valid, since there's no built-in revocation mechanism.

### Common Pitfalls

- No revocation: once issued, a JWT is valid until it expires — you can't invalidate it server-side without extra infrastructure (blocklists, short expiry + refresh tokens).
- Algorithm confusion attacks: always validate `alg` server-side; never trust the client-supplied algorithm.
- Storing sensitive data in payload: it's readable by anyone with the token.
- Long-lived tokens: typically paired with short-lived access tokens + longer-lived refresh tokens to balance security and UX.

Want me to show a code example (e.g., signing/verifying with a library like `jsonwebtoken` in Node or `PyJWT` in Python)?
