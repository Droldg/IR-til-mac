$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

$logPath = Join-Path $PSScriptRoot "listener.log"
$port = "COM3"

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python -and $python.Source -notlike "*\WindowsApps\python.exe") {
    & $python.Source listener.py --port $port *> $logPath
    exit $LASTEXITCODE
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    & $py.Source -3 listener.py --port $port *> $logPath
    exit $LASTEXITCODE
}

throw "Python was not found. Install Python, then run: pip install -r requirements.txt"
