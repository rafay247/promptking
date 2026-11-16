Here's a straightforward email validator for JS:

```javascript
function isValidEmail(email) {
  if (typeof email !== 'string') return false;

  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email.trim());
}
```

Usage:

```javascript
isValidEmail('user@example.com');     // true
isValidEmail('user@sub.domain.com');  // true
isValidEmail('not-an-email');         // false
isValidEmail('user@domain');          // false
```

Notes:
- This regex covers the common case (something@something.tld) without trying to fully implement RFC 5322, which is notoriously complex and mostly overkill in practice.
- If you need stricter/more complete validation (length limits, IP-literal domains, quoted local parts, etc.), use a maintained library instead of hand-rolling a regex — e.g. `validator.js`'s `isEmail()`.
- For most real-world use cases, the best "validation" is actually sending a confirmation email — regex just catches obvious typos before that.
