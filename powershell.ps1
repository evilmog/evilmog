# Mogs collection of powershell crap
Write-Host "Powershell Transcription Logging:" [Bool](Get-ItemProperty 'HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\Transcription' -ErrorAction SilentlyContinue).EnableTranscripting
Write-Host "Powershell Module Logging:" [Bool](Get-ItemProperty 'HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\Power Shell\ModuleLogging' -ErrorAction SilentlyContinue).EnableModuleLogging
Write-Host "Script Block Logging:" [Bool](Get-ItemProperty 'HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\Power Shell\ScriptBlockLogging' -ErrorAction SilentlyContinue).EnableScriptBlockLogging
Write-Host "Powershell Version" (Get-ItemProperty HKLM:\SOFTWARE\Microsoft\PowerShell*\PowerShellEngine -Name PowerShellVersion).PowerShellVersion
Write-Host "Powershell 2 Enabled:" (Test-Path $env:windir\Microsoft.Net\Framework\v2.0.50727\System.dll)
Write-Host "Powershell 5 Enabled:" (Test-Path $env:windir\Microsoft.Net\Framework\v4.0.30319\System.dll)
Write-Host "Legacy Task Scheduling Enabled:" [Bool](Get-ItemProperty 'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Configuration' -ErrorAction SilentlyContinue).EnableAt
Write-Host "Machine Password Change Disabled:" (Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\Netlogon\Parameters).DisablePasswordChange
Write-Host "Maximum Machine Password Age:" (Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\NetLogon\Parameters).MaximumPasswordAge
Write-Host "HKCU Always Install Elevated:" [Bool](Get-ItemProperty 'HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Installer' -ErrorAction SilentlyContinue).AlwaysInstallElevated
Write-Host "HKLM Always Install Elevated:" [Bool](Get-ItemProperty 'HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Installer' -ErrorAction SilentlyContinue).AlwaysInstallElevated
