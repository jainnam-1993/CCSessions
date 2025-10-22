# DAIC command to toggle between Discussion and Implementation modes (PowerShell version)

# Get the project root (where .claude directory is)
$ProjectRoot = Get-Location

while (-not (Test-Path (Join-Path $ProjectRoot ".claude")) -and $ProjectRoot.Path -ne $ProjectRoot.Root) {
    $ProjectRoot = Split-Path $ProjectRoot -Parent
}

if (-not (Test-Path (Join-Path $ProjectRoot ".claude"))) {
    Write-Host "[DAIC Error] Could not find .claude directory in current path or parent directories" -ForegroundColor Red
    exit 1
}

# Use central hooks from CC_SESSIONS_PATH
if (-not $env:CC_SESSIONS_PATH) {
    Write-Host "[DAIC Error] CC_SESSIONS_PATH environment variable not set" -ForegroundColor Red
    exit 1
}

$HooksDir = Join-Path $env:CC_SESSIONS_PATH "hooks"

# Check if Python is available
$PythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
} else {
    Write-Host "[DAIC Error] Python not found. Please ensure Python is installed and in your PATH" -ForegroundColor Red
    exit 1
}

# Run Python inline to toggle mode
$pythonScript = @"
import sys
sys.path.insert(0, r'$HooksDir')
from shared_state import toggle_daic_mode
mode = toggle_daic_mode()
print('[DAIC] ' + mode)
"@

& $PythonCmd -c $pythonScript