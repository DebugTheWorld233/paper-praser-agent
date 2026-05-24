#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/skills/paper-solution-agent"
DEST_ROOT="$CODEX_HOME/skills"
DEST="$DEST_ROOT/paper-solution-agent"

if [ ! -f "$SRC/SKILL.md" ]; then
  echo "Cannot find source skill: $SRC" >&2
  exit 1
fi

mkdir -p "$DEST_ROOT"
rm -rf "$DEST"
mkdir -p "$DEST"
cp "$SRC/SKILL.md" "$DEST/SKILL.md"

echo "Installed paper-solution-agent to $DEST"
echo "Restart Codex to pick up the new skill."
echo "Uninstall by removing $DEST"
