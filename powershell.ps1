# Mogs collection of powershell crap
[Bool](Get-ItemProperty 'HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\Transcription' -ErrorAction SilentlyContinue).EnableTranscripting
[Bool](Get-ItemProperty 'HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\Power Shell\ModuleLogging' -ErrorAction SilentlyContinue).EnableModuleLogging
[Bool](Get-ItemProperty 'HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\Power Shell\ScriptBlockLogging' -ErrorAction SilentlyContinue).EnableScriptBlockLogging
(Get-ItemProperty HKLM:\SOFTWARE\Microsoft\PowerShell*\PowerShellEngine -Name PowerShellVersion).PowerShellVersion
(Test-Path $env:windir\Microsoft.Net\Framework\v2.0.50727\System.dll)
(Test-Path $env:windir\Microsoft.Net\Framework\v4.0.30319\System.dll)
Get-WMIObject –Class Win32_Product | ?{$_.Vendor -notmatch 'Microsoft'}
[Bool](Get-ItemProperty 'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Configuration' -ErrorAction SilentlyContinue).EnableAt
(Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\Netlogon\Parameters).DisablePasswordChange
(Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\NetLogon\Parameters).MaximumPasswordAge

