#!/usr/bin/env bash
# Run one headless Claude Code step: first on the Max subscription (CLAUDE_CODE_OAUTH_TOKEN); if that run stops on
# the subscription usage limit and ANTHROPIC_API_KEY_BACKUP is set, rerun the same step on the pay-as-you-go API key.
# The rerun resumes from the files the first run left behind (the prompts resume from the episode's stage).
#   pipeline/claude_run.sh <out.jsonl> <max_turns> <prompt>
# Claude Code prefers ANTHROPIC_API_KEY over the OAuth token when both are set, so the key is only exported for the
# fallback run; the backup secret lives under a different name so the subscription is always tried first.
set -uo pipefail
out=$1; turns=$2; prompt=$3

run() {
  claude -p "$prompt" --dangerously-skip-permissions --max-turns "$turns" \
    --output-format stream-json --verbose < /dev/null > "$out"
}

limit_hit() {  # the final stream-json "result" line says the run ended on a usage limit
  python - "$out" <<'EOF'
import json, re, sys
last = {}
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    try:
        d = json.loads(line)
    except ValueError:
        continue
    if d.get("type") == "result":
        last = d
text = str(last.get("result", "")) + " " + str(last.get("errors", ""))
hit = re.search(r"hit your .{0,30}limit|usage limit|limit reached|limit · resets|rate_limit", text, re.I)
sys.exit(0 if (last.get("is_error") or not last) and hit else 1)
EOF
}

if [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
  ( unset ANTHROPIC_API_KEY; run ); rc=$?
  limit_hit || exit $rc
  echo "Claude subscription usage limit hit."
  cp "$out" "${out%.jsonl}.subscription.jsonl"
fi

if [ -z "${ANTHROPIC_API_KEY_BACKUP:-}" ]; then
  python -m studio notify "⛔ Claude usage limit hit and no backup API key is set; step skipped. ${RUN_URL:-}" || true
  exit 1
fi

python -m studio notify "💳 Claude subscription limit hit: this step is continuing on the backup API key (pay-as-you-go). ${RUN_URL:-}" || true
export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY_BACKUP"
unset CLAUDE_CODE_OAUTH_TOKEN
run
