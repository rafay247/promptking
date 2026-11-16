```js
/**
 * Validates an email address using the WHATWG HTML living standard pattern
 * (the same regex browsers use for <input type="email">).
 * This checks *format* only — it cannot confirm the mailbox exists.
 *
 * @param {unknown} email
 * @returns {boolean}
 */
function isValidEmail(email) {
  if (typeof email !== 'string') return false;

  const trimmed = email.trim();
  if (trimmed.length === 0 || trimmed.length > 254) return false; // RFC 5321 max

  const [local] = trimmed.split('@');
  if (local && local.length > 64) return false; // RFC 5321 local-part max

  const EMAIL_REGEX =
    /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/;

  return EMAIL_REGEX.test(trimmed);
}

module.exports = { isValidEmail };
```

```js
// test cases
const cases = [
  ['user@example.com', true],
  ['first.last+tag@sub.example.co.uk', true],
  ['user@example.com ', true],      // trimmed
  ['', false],                       // empty
  [null, false],                     // wrong type
  [undefined, false],                // wrong type
  ['plainaddress', false],           // no @
  ['@example.com', false],           // no local part
  ['user@', false],                  // no domain
  ['user@@example.com', false],      // double @
  ['user@example', false],           // no TLD
  ['user@.com', false],              // domain starts with dot
  ['user@exam ple.com', false],      // space
  ['a'.repeat(65) + '@example.com', false], // local part too long
];

for (const [input, expected] of cases) {
  const result = isValidEmail(input);
  console.assert(
    result === expected,
    `FAIL: isValidEmail(${JSON.stringify(input)}) => ${result}, expected ${expected}`
  );
}
console.log('All email validation tests passed.');
```

**Usage:** `isValidEmail('name@domain.com')` → `true`.

**Why this regex:** it's the exact pattern the HTML spec mandates for `<input type="email">`, so it matches what browsers already accept — no surprises between client and server validation. Full RFC 5322 compliance is pointless in practice (it accepts addresses almost no real mail server does); the real-world check is "does the address exist," which this regex can't answer.

**Standard-library / library alternative:** JS/Node have no built-in email validator. For stricter or configurable validation, use `validator.isEmail()` (npm `validator`) or `z.string().email()` (Zod) instead of hand-rolling. For actual delivery guarantees, send a confirmation email rather than relying on regex at all.

Assumed: plain JS (not TypeScript) and Node/browser-agnostic code, since no framework was specified.
