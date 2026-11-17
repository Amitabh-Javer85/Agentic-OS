<#
.SYNOPSIS
    Windows Task Scheduler runner for Agentic OS routines.
.DESCRIPTION
    Triggers a registered skill headlessly via the local runner or directly via python.
.EXAMPLE
    .\run-routine.ps1 -SkillName "weekly-digest"
#>
param (
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9-]+$')]
    [string]$SkillName,
    [string]$PythonExe = 'python.exe'
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Split-Path -Parent $ScriptDir

Set-Location $WorkspaceRoot

Write-Host "[Agentic OS] Triggering routine '$SkillName' at $(Get-Date -Format o)"

# Run directly through runner CLI dispatcher
if (Test-Path "$WorkspaceRoot\.venv\Scripts\python.exe") {
    $PythonExe = "$WorkspaceRoot\.venv\Scripts\python.exe"
}

& $PythonExe "$WorkspaceRoot\apps\runner\server.py" trigger $SkillName
$ExitCode = $LASTEXITCODE

if ($ExitCode -eq 0) {
    Write-Host "[Agentic OS] Routine '$SkillName' completed successfully."
} else {
    [Console]::Error.WriteLine("[Agentic OS] Routine '$SkillName' failed with exit code $ExitCode.")
}

exit $ExitCode
