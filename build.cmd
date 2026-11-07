@echo off
setlocal
set "CT3_ROOT=%~dp0"
set "CT3_CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not exist "%CT3_CSC%" exit /b 1
if not exist "%CT3_ROOT%dist" mkdir "%CT3_ROOT%dist"
"%CT3_CSC%" /nologo /target:winexe /platform:anycpu /optimize+ /debug- /langversion:5 /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll "/win32manifest:%CT3_ROOT%src\native\app.manifest" "/resource:%CT3_ROOT%patches\CT3-Korean-v1.0.ct3patch,CT3.patch" "/out:%CT3_ROOT%dist\XBOX-Crazy-Taxi-3-Kr-v1.0.1-Patcher.exe" "%CT3_ROOT%src\native\PatchEngine.cs" "%CT3_ROOT%src\native\Program.cs"
if errorlevel 1 exit /b 1
"%CT3_ROOT%dist\XBOX-Crazy-Taxi-3-Kr-v1.0.1-Patcher.exe" --self-test
exit /b %ERRORLEVEL%
