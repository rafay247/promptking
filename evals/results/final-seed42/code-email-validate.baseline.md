Here's a practical email validator using a regex that balances correctness with simplicity (full RFC 5322 compliance is overkill for almost all use cases):

```js
function isValidEmail(email) {
  if (typeof email !== 'string') return false;

  const trimmed = email.trim();
  if (trimmed.length === 0 || trimmed.length > 254) return false;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(trimmed)) return false;

  const [localPart, domain] = trimmed.split('@');
  if (localPart.length > 64) return false;
  if (domain.split('.').some(label => label.length === 0 || label.length > 63)) return false;

  return true;
}
```

Usage:

```js
isValidEmail('development.nexuscabs@gmail.com'); // true
isValidEmail('not-an-email');                     // false
isValidEmail('a@b.c');                            // true
isValidEmail('a@b');                              // false (no TLD)
```

Notes:
- This catches the vast majority of malformed input without trying to fully implement RFC 5322 (which permits bizarre-but-technically-legal addresses like `"quoted string"@example.com`).
- Length checks mirror the real limits (254 total, 64 for local part, 63 per domain label).
- If you need to confirm the address actually *receives* mail, no regex can do that — you'd need to send a verification email.
