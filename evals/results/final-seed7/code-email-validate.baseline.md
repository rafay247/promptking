Here's a solid email validation function in JavaScript:

```js
function isValidEmail(email) {
  if (typeof email !== 'string') return false;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email.trim());
}
```

**Usage:**
```js
isValidEmail('user@example.com');      // true
isValidEmail('user.name+tag@sub.co');  // true
isValidEmail('invalid');               // false
isValidEmail('missing@tld');           // false
isValidEmail('@example.com');          // false
```

Notes:
- This regex is intentionally simple — it checks for "something@something.something" without spaces. Fully RFC 5322-compliant validation is extremely complex (the spec allows quoted strings, comments, IP-literal domains, etc.) and not practical to implement by hand.
- For production use where correctness really matters (e.g., signup forms), consider:
  - Using the browser's built-in `<input type="email">` validation for UI forms.
  - Using a well-tested library like [validator.js](https://github.com/validatorjs/validator.js) (`isEmail()`).
  - Always pairing syntactic validation with a confirmation email to verify the address actually works — no regex can confirm deliverability.
