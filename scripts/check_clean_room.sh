#!/usr/bin/env bash
# Clean-room sanity check.
#
# Looks for obvious forbidden artifacts: secret-like filenames, private key
# material, common credential formats, and a tracked .env file. This is a
# pre-commit sanity check, NOT a substitute for real secret scanning or a
# security review.
set -uo pipefail

cd "$(dirname "$0")/.."

violations=0

note() {
  echo "CLEAN-ROOM VIOLATION: $1"
  violations=1
}

if git rev-parse --git-dir >/dev/null 2>&1; then
  files=$(git ls-files)
else
  files=$(find . -type f -not -path './.git/*' -not -path './.venv/*' | sed 's|^\./||')
fi

# 1. Forbidden filename patterns.
while IFS= read -r f; do
  base=$(basename "$f" | tr '[:upper:]' '[:lower:]')
  case "$base" in
    *.pem|*.key|*.p12|*.pfx|*secret*|*token*|*credential*|*password*|*apikey*|id_rsa*|id_ed25519*)
      note "forbidden filename: $f"
      ;;
  esac
done <<< "$files"

# 2. A real .env must never be tracked.
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  note ".env is tracked by git — remove it (only .env.example belongs in the repo)"
fi

# 3. Secret-like content patterns.
content_patterns=(
  'BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY'
  'AKIA[0-9A-Z]{16}'
  'sk-[A-Za-z0-9]{32,}'
  'ghp_[A-Za-z0-9]{36}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
)
for pattern in "${content_patterns[@]}"; do
  matches=$(echo "$files" | grep -v '^scripts/check_clean_room.sh$' \
    | xargs -I{} grep -lE "$pattern" "{}" 2>/dev/null)
  if [ -n "$matches" ]; then
    note "secret-like content matching '$pattern' in: $(echo "$matches" | tr '\n' ' ')"
  fi
done

if [ "$violations" -ne 0 ]; then
  echo ""
  echo "Clean-room check FAILED. Remove the artifacts above before committing."
  exit 1
fi

echo "Clean-room check passed."
