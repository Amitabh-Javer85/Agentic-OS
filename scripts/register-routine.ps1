<# Register the weekly digest for the current logged-on user, without credentials. #>
[CmdletBinding(SupportsShouldProcess)]
param([string]$At = '09:00')
$ErrorActionPreference = 'Stop'
$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
$TaskName = 'AgenticOS-WeeklyDigest'
$PowerShellExe = (Get-Command powershell.exe -ErrorAction Stop).Source
$PythonExe = (Get-Command python.exe -ErrorAction Stop).Source
$UserId = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$Arguments = '-NoProfile -NonInteractive -File "{0}" -SkillName weekly-digest -PythonExe "{1}"' -f (Join-Path $PSScriptRoot 'run-routine.ps1'), $PythonExe
$Action = New-ScheduledTaskAction -Execute $PowerShellExe -Argument $Arguments -WorkingDirectory $WorkspaceRoot
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At $At
$Principal = New-ScheduledTaskPrincipal -UserId $UserId -LogonType Interactive -RunLevel Limited
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
if ($PSCmdlet.ShouldProcess($TaskName, 'Register Friday routine for the current interactive user')) {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description 'Agentic OS weekly digest; requires user sign-in and authenticated Claude CLI.' -Force | Out-Null
    $Task = Get-ScheduledTask -TaskName $TaskName
    if ($Task.State -ne 'Ready') { throw "Task registration returned state $($Task.State)" }
    $Task | Select-Object TaskName, State
}
