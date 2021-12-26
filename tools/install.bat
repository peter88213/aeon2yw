set app=aeon2yw

set oldappdir="%APPDATA%\PyWriter\%app%"
set basedir="%USERPROFILE%\.pywriter"
if not exist %basedir% md %basedir%
set appdir="%USERPROFILE%\.pywriter\%app%"

if not exist %oldappdir% goto label1 
move %oldappdir% %appdir%
if exist %USERPROFILE%\Desktop\%app%.lnk del %USERPROFILE%\Desktop\%app%.lnk

:label1
if not exist %appdir% md %appdir%

copy %app%.pyw %appdir%

set cnfdir="%USERPROFILE%\.pywriter\%app%\config"
if not exist %cnfdir% md %cnfdir%

rem copy /Y sample\aeon2yw.ini %cnfdir%

set aeon2dir="%LOCALAPPDATA%\Scribble Code\Aeon Timeline 2\CustomTemplates"
if exist %aeon2dir% copy /Y sample\yWriter.xml %aeon2dir%

if exist %USERPROFILE%\Desktop\%app%.lnk goto end

@echo off
cls
echo The %app% program is installed.
echo Now create a shortcut on your desktop. 
echo For this, hold down the Alt key on your keyboard and then drag and drop %app%.pyw to your desktop. 
@echo off
explorer %appdir%\
pause

:end
