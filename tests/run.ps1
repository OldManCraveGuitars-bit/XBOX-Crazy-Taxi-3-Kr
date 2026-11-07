$ErrorActionPreference = 'Stop'
$ct3Root = Split-Path -Parent $PSScriptRoot
$ct3Compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
New-Item -ItemType Directory -Path "$ct3Root\build" -Force | Out-Null
& $ct3Compiler /nologo /target:exe /main:NativeTests /langversion:5 `
    /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll `
    "/out:$ct3Root\build\NativeTests.exe" `
    "$ct3Root\src\native\PatchEngine.cs" "$ct3Root\src\native\Program.cs" "$PSScriptRoot\NativeTests.cs"
if ($LASTEXITCODE -ne 0) { throw 'Test compilation failed.' }
& "$ct3Root\build\NativeTests.exe"
if ($LASTEXITCODE -ne 0) { throw 'Native tests failed.' }
