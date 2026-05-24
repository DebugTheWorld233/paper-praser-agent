param(
    [string]$ClaudeHome = $(if ($env:CLAUDE_HOME) { $env:CLAUDE_HOME } else { Join-Path $HOME ".claude" })
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$src = Join-Path $repoRoot "adapters\claude-code\paper-solution-agent.md"
$destRoot = Join-Path $ClaudeHome "commands"
$dest = Join-Path $destRoot "paper-solution-agent.md"

if (-not (Test-Path $src)) {
    throw "Cannot find Claude Code command template: $src"
}

New-Item -ItemType Directory -Force $destRoot | Out-Null
Copy-Item -LiteralPath $src -Destination $dest -Force

Write-Host "Installed Claude Code command to $dest"
Write-Host "Restart Claude Code or open a new session to pick up /paper-solution-agent."
Write-Host "Uninstall by removing $dest"
