$ErrorActionPreference = "Stop"

$listenerDir = $PSScriptRoot
$startupDir = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupDir "Pico IR listener.lnk"
$targetPath = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$scriptPath = Join-Path $listenerDir "start_listener_windows.ps1"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
$shortcut.WorkingDirectory = $listenerDir
$shortcut.WindowStyle = 7
$shortcut.Description = "Start Pico IR shutdown listener"
$shortcut.Save()

Write-Host "Created startup shortcut:"
Write-Host $shortcutPath
