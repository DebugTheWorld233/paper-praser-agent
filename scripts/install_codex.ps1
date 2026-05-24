param(
    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" })
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$src = Join-Path $repoRoot "skills\paper-solution-agent"
$destRoot = Join-Path $CodexHome "skills"
$dest = Join-Path $destRoot "paper-solution-agent"

if (-not (Test-Path (Join-Path $src "SKILL.md"))) {
    throw "Cannot find source skill: $src"
}

New-Item -ItemType Directory -Force $destRoot | Out-Null

if (Test-Path $dest) {
    Remove-Item -LiteralPath $dest -Recurse -Force
}

New-Item -ItemType Directory -Force $dest | Out-Null
Copy-Item -LiteralPath (Join-Path $src "SKILL.md") -Destination (Join-Path $dest "SKILL.md") -Force

Write-Host "Installed paper-solution-agent to $dest"
Write-Host "Restart Codex to pick up the new skill."
Write-Host "Uninstall by removing $dest"
