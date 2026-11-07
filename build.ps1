$ErrorActionPreference = 'Stop'
$ct3Root = $PSScriptRoot
$ct3Compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $ct3Compiler)) { throw 'Windows .NET Framework C# compiler is required.' }
$ct3Manifest = Get-Content -LiteralPath "$ct3Root\patches\manifest.json" -Raw | ConvertFrom-Json
$ct3PatchHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "$ct3Root\patches\CT3-Korean-v1.0.ct3patch").Hash.ToLowerInvariant()
if ($ct3PatchHash -ne $ct3Manifest.native_patch.sha256) { throw 'Patch SHA-256 mismatch.' }
if (-not (Get-Content -LiteralPath "$ct3Root\src\native\Program.cs" -Raw).Contains($ct3PatchHash)) { throw 'Embedded patch hash constant mismatch.' }
$ct3Output = Join-Path $ct3Root 'dist'
New-Item -ItemType Directory -Path $ct3Output -Force | Out-Null
& $ct3Compiler /nologo /target:winexe /platform:anycpu /optimize+ /debug- /langversion:5 `
    /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll `
    "/win32manifest:$ct3Root\src\native\app.manifest" `
    "/resource:$ct3Root\patches\CT3-Korean-v1.0.ct3patch,CT3.patch" `
    "/out:$ct3Output\XBOX-Crazy-Taxi-3-Kr-v1.0.1-Patcher.exe" `
    "$ct3Root\src\native\PatchEngine.cs" "$ct3Root\src\native\Program.cs"
if ($LASTEXITCODE -ne 0) { throw 'C# compilation failed.' }
