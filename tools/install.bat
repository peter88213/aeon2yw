set app=aeon2yw
set basedir="%APPDATA%\PyWriter"
if not exist %basedir% md %basedir%
set appdir="%APPDATA%\PyWriter\%app%"
if not exist %appdir% md %appdir%
copy %app%.pyw %appdir%

set cnfdir="%APPDATA%\PyWriter\%app%\config"
if not exist %cnfdir% md %cnfdir%

copy /Y sample\aeon2yw.ini %cnfdir%

set aeon2dir="%LOCALAPPDATA%\Scribble Code\Aeon Timeline 2\CustomTemplates"
if exist %aeon2dir% copy /Y sample\yWriter.xml %aeon2dir%

if exist %USERPROFILE%\Desktop\%app%.lnk goto :end

@echo off
cls
echo The %app% program is installed.
echo Now create a shortcut on your desktop. 
echo For this, hold down the Alt key on your keyboard and then drag and drop %app%.pyw to your desktop. 
@echo off
explorer "%APPDATA%\PyWriter\%app%\"
pause

:end
