# Per-skill wrapper. Delegates to repo-root installer with --skill <this-dir-name>.
$ErrorActionPreference = 'Stop'

$skillDir  = $PSScriptRoot
$repoRoot  = (Resolve-Path (Join-Path $skillDir '..\..')).Path
$skillName = Split-Path $skillDir -Leaf
$rootInstaller = Join-Path $repoRoot 'install.ps1'

& $rootInstaller --skill $skillName @args
exit $LASTEXITCODE
