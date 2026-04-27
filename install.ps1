# Wrapper for install.py. Locates Python and forwards args.
$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
$installer = Join-Path $scriptDir 'install.py'

function Resolve-Python {
    $candidates = @(
        @{ Cmd = 'py';     Args = @('-3') },
        @{ Cmd = 'python'; Args = @() },
        @{ Cmd = 'python3'; Args = @() }
    )
    foreach ($c in $candidates) {
        $found = Get-Command $c.Cmd -ErrorAction SilentlyContinue
        if ($found) { return $c }
    }
    return $null
}

$py = Resolve-Python
if (-not $py) {
    Write-Error "python not found. install Python 3.8+ from https://www.python.org/downloads/ and re-run."
    exit 1
}

& $py.Cmd @($py.Args + @($installer) + $args)
exit $LASTEXITCODE
