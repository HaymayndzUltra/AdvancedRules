#!/usr/bin/env bash
set -euo pipefail

FILE="${1:-tools/envelopes/action_envelope.json}"
# Backward compatibility: if caller passed legacy path and it's missing, use new location
if [[ ! -f "$FILE" && "${1:-}" == "action_envelope.json" && -f "tools/envelopes/action_envelope.json" ]]; then
  FILE="tools/envelopes/action_envelope.json"
fi
if [[ ! -f "$FILE" ]]; then
  echo "ERR: envelope not found: $FILE"
  exit 1
fi

decision=$(jq -r '.decision // empty' "$FILE")
type=$(jq -r '.candidate.action_type // empty' "$FILE")
id=$(jq -r '.chosen_id // empty' "$FILE")
cmd=$(jq -r '.candidate.command // empty' "$FILE")

echo "[ENVELOPE] decision=$decision id=$id type=${type:-N/A}"

case "$type" in
  NATURAL_STEP)
    echo "PLAN_ONLY: open next_prompt_for_cursor.md in Cursor and execute plan."
    exit 0
    ;;
  COMMAND_TRIGGER)
    if [[ -z "$cmd" ]]; then
      echo "DRY_RUN: no command attached for candidate '$id'. Add .candidate.command first."
      exit 2
    fi
    echo "DRY_RUN PREVIEW:"
    echo "$cmd"
    echo
    echo "Safety: command not executed. Review and run manually if approved."
    exit 0
    ;;
  *)
    echo "Unknown action_type: ${type:-<none>}"
    exit 3
    ;;
esac
