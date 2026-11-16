#!/bin/sh
# PromptKing always-on hook (UserPromptSubmit).
# Adds context only while the flag file exists. Fails open: never blocks a prompt.
cat >/dev/null 2>&1
FLAG="${XDG_CONFIG_HOME:-$HOME/.config}/promptking/always-on"
[ -f "$FLAG" ] || exit 0
printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"PromptKing always-on mode is enabled. Handle this message with the promptking skill (Decode, Brief, Execute, Verify, Deliver) unless it is a slash command, a short acknowledgement, or a direct answer to a question you just asked."}}'
exit 0
