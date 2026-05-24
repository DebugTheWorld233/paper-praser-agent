#!/usr/bin/env bash
set -euo pipefail

CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/adapters/claude-code/paper-solution-agent.md"
DEST_ROOT="$CLAUDE_HOME/commands"
DEST="$DEST_ROOT/paper-solution-agent.md"

if [ ! -f "$SRC" ]; then
  echo "Cannot find Claude Code command template: $SRC" >&2
  exit 1
fi

mkdir -p "$DEST_ROOT"
cp "$SRC" "$DEST"

echo "Installed Claude Code command to $DEST"
echo "Restart Claude Code or open a new session to pick up /paper-solution-agent."
echo "Uninstall by removing $DEST"
