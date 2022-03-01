#!/usr/bin/env python3
"""Install the aeon2yw script. 

Version @release

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
import stat
from shutil import copyfile
from pathlib import Path
from string import Template
try:
    from tkinter import *
    from tkinter import messagebox
except ModuleNotFoundError:
    print('The tkinter module is missing. Please install the tk support package for your python3 version.')
    sys.exit(1)

APPNAME = 'aeon2yw'
VERSION = ' @release'
APP = f'{APPNAME}.pyw'
INI_FILE = f'{APPNAME}.ini'
INI_PATH = '/config/'
SAMPLE_PATH = 'sample/'
SUCCESS_MESSAGE = '''

$Appname is installed here:

$Apppath'''

SHORTCUT_MESSAGE = '''
Now you might want to create a shortcut on your desktop.  

On Windows, open the installation folder, hold down the Alt key on your keyboard, 
and then drag and drop $Appname.pyw to your desktop.

On Linux, create a launcher on your desktop. With xfce for instance, the launcher's command may look like this:
python3 '$Apppath' %F
'''

root = Tk()
processInfo = Label(root, text='')
message = []

SET_CONTEXT_MENU = '''Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\SOFTWARE\Classes\\yWriter7\\shell\\Sync with Aeon Timeline 2]

[HKEY_CURRENT_USER\SOFTWARE\Classes\\yWriter7\\shell\\Sync with Aeon Timeline 2\\command]
@="\\"${PYTHON}\\" \\"${SCRIPT}\\" \\"%1\\""

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\.aeonzip]
@="Aeon2Project"

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\Aeon2Project]
@="Aeon Timeline 2 Project"

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\Aeon2Project\\DefaultIcon]
@="C:\\\\Program Files (x86)\\\\Aeon Timeline 2\\\\AeonTimeline2.exe,0"

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\Aeon2Project\\shell\\open]

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\Aeon2Project\\shell\\open\\command]
@="\\"C:\\\\Program Files (x86)\\\\Aeon Timeline 2\\\\AeonTimeline2.exe\\" \\"%1\\""

[HKEY_CURRENT_USER\SOFTWARE\Classes\\Aeon2Project\\shell\\Sync with yWriter]

[HKEY_CURRENT_USER\SOFTWARE\Classes\\Aeon2Project\\shell\\Sync with yWriter\\command]
@="\\"${PYTHON}\\" \\"${SCRIPT}\\" \\"%1\\""
'''

RESET_CONTEXT_MENU = '''Windows Registry Editor Version 5.00

[-HKEY_CURRENT_USER\\SOFTWARE\\Classes\\yWriter7\\shell\Sync with Aeon Timeline 2]
[-HKEY_CURRENT_USER\\SOFTWARE\\Classes\\Aeon2Project]
'''

def output(text):
    message.append(text)
    processInfo.config(text=('\n').join(message))

def make_context_menu(installPath):
    """Generate ".reg" files to extend the yWriter and Timeline context menus."""

    def save_reg_file(filePath, template, mapping):
        """Save a registry file."""
        with open(filePath, 'w', encoding='utf-8') as f:
            f.write(template.safe_substitute(mapping))
        output(f'Creating "{os.path.normpath(filePath)}"')
    python = sys.executable.replace('\\', '\\\\')
    instPath = installPath.replace('/', '\\\\')
    script = f'{instPath}\\\\{APP}'
    mapping = dict(PYTHON=python, SCRIPT=script)
    save_reg_file(f'{installPath}/add_context_menu.reg', Template(SET_CONTEXT_MENU), mapping)
    save_reg_file(f'{installPath}/rem_context_menu.reg', Template(RESET_CONTEXT_MENU), {})

def open_folder(installDir):
    """Open an installation folder window in the file manager.
    """
    try:
        os.startfile(os.path.normpath(installDir))
        # Windows
    except:
        try:
            os.system('xdg-open "%s"' % os.path.normpath(installDir))
            # Linux
        except:
            try:
                os.system('open "%s"' % os.path.normpath(installDir))
                # Mac
            except:
                pass


def install(pywriterPath):
    """Install the script."""

    # Create a general PyWriter installation directory, if necessary.
    os.makedirs(pywriterPath, exist_ok=True)
    installDir = f'{pywriterPath}{APPNAME}'
    cnfDir = f'{installDir}{INI_PATH}'
    if os.path.isfile(f'{installDir}/{APP}'):
        simpleUpdate = True
    else:
        simpleUpdate = False
    try:
        # Move an existing installation to the new place, if necessary.
        oldHome = os.getenv('APPDATA').replace('\\', '/')
        oldInstDir = f'{oldHome}/pyWriter/{APPNAME}'
        os.replace(oldInstDir, installDir)
        output(f'Moving "{oldInstDir}" to "{installDir}"')
    except:
        pass
    os.makedirs(cnfDir, exist_ok=True)

    # Delete the old version, but retain configuration, if any.
    with os.scandir(installDir) as files:
        for file in files:
            if not 'config' in file.name:
                os.remove(file)
                output(f'Removing "{file.name}"')

    # Install the new version.
    copyfile(APP, f'{installDir}/{APP}')
    output(f'Copying "{APP}"')

    # Make the script executable under Linux.
    st = os.stat(f'{installDir}/{APP}')
    os.chmod(f'{installDir}/{APP}', st.st_mode | stat.S_IEXEC)

    # Install a configuration file, if needed.
    try:
        if not os.path.isfile(f'{cnfDir}{file.name}'):
            copyfile(f'{SAMPLE_PATH}{file.name}', f'{cnfDir}{file.name}')
            output(f'Copying "{INI_FILE}"')
        else:
            output(f'Keeping "{INI_FILE}"')
    except:
        pass

    # Install the Aeon2 sample template, if needed.
    try:
        appDataLocal = os.getenv('LOCALAPPDATA').replace('\\', '/')
        aeon2dir =  f'{appDataLocal}/Scribble Code/Aeon Timeline 2/CustomTemplates/'
        sampleTemplate = 'yWriter.xml'
        if not os.path.isfile(aeon2dir + sampleTemplate):
            copyfile(f'{SAMPLE_PATH}{sampleTemplate}', f'{aeon2dir}{sampleTemplate}')
            output(f'Copying "{sampleTemplate}"')
        else:
            if messagebox.askyesno('Aeon Timeline 2 "yWriter" template', f'Update "{aeon2dir}{sampleTemplate}"?'):
                copyfile(f'{SAMPLE_PATH}{sampleTemplate}',f'{aeon2dir}{sampleTemplate}')
                output(f'Updating "{sampleTemplate}"')
            else:
                output(f'Keeping "{sampleTemplate}"')
    except:
        pass

    # Generate registry entries for the context menu (Windows only).
    if os.name == 'nt':
        make_context_menu(installDir)

    # Display a success message.
    mapping = {'Appname': APPNAME, 'Apppath': f'{installDir}/{APP}'}
    output(Template(SUCCESS_MESSAGE).safe_substitute(mapping))

    # Ask for shortcut creation.
    if not simpleUpdate:
        output(Template(SHORTCUT_MESSAGE).safe_substitute(mapping))


if __name__ == '__main__':

    # Open a tk window.
    root.geometry("800x600")
    root.title(f'Install {APPNAME}{VERSION}')
    header = Label(root, text='')
    header.pack(padx=5, pady=5)

    # Prepare the messaging area.
    processInfo.pack(padx=5, pady=5)

    # Run the installation.
    homePath = str(Path.home()).replace('\\', '/')
    install(f'{homePath}/.pywriter/')

    # Show options: open installation folders or quit.
    root.openButton = Button(text="Open installation folder", command=lambda: open_folder(f'{homePath}/.pywriter/{APPNAME}'))
    root.openButton.config(height=1, width=30)
    root.openButton.pack(padx=5, pady=5)
    root.quitButton = Button(text="Quit", command=quit)
    root.quitButton.config(height=1, width=30)
    root.quitButton.pack(padx=5, pady=5)
    root.mainloop()
