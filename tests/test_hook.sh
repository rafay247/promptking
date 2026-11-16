#!/bin/sh
# Tests for hooks/always-on.sh. Run: sh tests/test_hook.sh
set -u
HOOK="$(cd "$(dirname "$0")/.." && pwd)/hooks/always-on.sh"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
fail=0

out=$(printf '{"prompt":"hi"}' | XDG_CONFIG_HOME="$T" sh "$HOOK"); rc=$?
if [ "$rc" -eq 0 ] && [ -z "$out" ]; then echo "PASS flag absent -> silent"; else echo "FAIL flag absent (rc=$rc out=$out)"; fail=1; fi

mkdir -p "$T/promptking" && touch "$T/promptking/always-on"
out=$(printf '{"prompt":"hi"}' | XDG_CONFIG_HOME="$T" sh "$HOOK"); rc=$?
if [ "$rc" -eq 0 ] && printf '%s' "$out" | python3 -c '
import json, sys
d = json.load(sys.stdin)["hookSpecificOutput"]
assert d["hookEventName"] == "UserPromptSubmit"
assert "promptking" in d["additionalContext"].lower()
'; then echo "PASS flag present -> context JSON"; else echo "FAIL flag present (rc=$rc out=$out)"; fail=1; fi

exit $fail
