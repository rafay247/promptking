```js
/**
 * Validates an email address format (syntax only — does not verify the mailbox exists).
 * @param {string} email
 * @returns {boolean}
 */
function isValidEmail(email) {
  if (typeof email !== 'string') return false;

  const trimmed = email.trim();
  if (trimmed.length === 0 || trimmed.length > 254) return false;

  // Practical RFC 5322-ish check: local@domain, no consecutive dots, valid TLD.
  const EMAIL_RE =
    /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/;

  if (!EMAIL_RE.test(trimmed)) return false;

  const [localPart] = trimmed.split('@');
  if (localPart.length > 64) return false;        // RFC 5321 local-part limit
  if (localPart.includes('..')) return false;      // no consecutive dots

  return true;
}

module.exports = { isValidEmail };
```

Test cases:

```js
const cases = [
  ['user@example.com', true],
  ['first.last+tag@sub.example.co.uk', true],
  ['', false],
  ['   ', false],
  ['no-at-sign.com', false],
  ['user@@example.com', false],
  ['user@.com', false],
  ['user..name@example.com', false],
  ['user@example', false],          // no TLD
  ['a'.repeat(65) + '@example.com', false], // local part too long
  [null, false],
  [undefined, false],
  [42, false],
];

for (const [input, expected] of cases) {
  const result = isValidEmail(input);
  console.log(result === expected ? 'PASS' : 'FAIL', JSON.stringify(input), '->', result);
}
```

This is syntax validation only — it won't catch a well-formed address that doesn't actually exist. To confirm deliverability, send a verification email or use an MX-lookup/verification API.

For a browser form, `<input type="email" required>` plus `el.checkValidity()` gives you free native validation and should usually be your first line of defense; use this function for server-side/API validation where you can't trust the client.

Assumed: you want pragmatic syntax validation (covers 99% of real-world cases), not a full RFC 5322 parser — those allow quoted strings and comments that no real mail provider issues anyway.
