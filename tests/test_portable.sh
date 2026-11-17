#!/bin/sh
# Checks the portable PromptKing prompt stays paste-ready for other AI tools.
# Run: sh tests/test_portable.sh
set -u
F="$(cd "$(dirname "$0")/.." && pwd)/portable/PROMPTKING.md"
fail=0
size=$(wc -c < "$F")
if [ "$size" -lt 8000 ]; then echo "PASS under 8000 chars ($size) for ChatGPT custom GPT instructions"; else echo "FAIL $size chars (limit 8000)"; fail=1; fi
for s in '/promptking' 'XDG_CONFIG_HOME' 'Claude Code' 'name: promptking' 'repo'; do
  if grep -q -- "$s" "$F"; then echo "FAIL contains tool-specific text: $s"; fail=1; else echo "PASS no '$s'"; fi
done
exit $fail
