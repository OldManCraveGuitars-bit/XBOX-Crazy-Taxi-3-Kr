@echo off
setlocal
set "CT3_ROOT=%~dp0.."
set "CT3_CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not exist "%CT3_ROOT%\build" mkdir "%CT3_ROOT%\build"
"%CT3_CSC%" /nologo /target:exe /main:NativeTests /langversion:5 /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll "/out:%CT3_ROOT%\build\NativeTests.exe" "%CT3_ROOT%\src\native\PatchEngine.cs" "%CT3_ROOT%\src\native\Program.cs" "%~dp0NativeTests.cs"
if errorlevel 1 exit /b 1
"%CT3_ROOT%\build\NativeTests.exe"
exit /b %ERRORLEVEL%
