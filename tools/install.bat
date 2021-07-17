set app=aeon2yw
set basedir="%APPDATA%\PyWriter"
if not exist %basedir% md %basedir%
set appdir="%APPDATA%\PyWriter\%app%"
if not exist %appdir% md %appdir%
copy %app%.py %appdir%

set TARGET='%APPDATA%\PyWriter\%app%\%app%.py'
set SHORTCUT='%USERPROFILE%\desktop\%app%.lnk'
set PWS=powershell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile

%PWS% -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(%SHORTCUT%); $S.TargetPath = %TARGET%; $S.Save()"

rem set cnfdir="%APPDATA%\PyWriter\%app%\config"
rem if not exist %cnfdir% md %cnfdir%
rem echo "N" | copy/-Y sample\%app%\*.* %cnfdir%
