"""Aeon Timeline 2 sync plugin for novelyst.

Version @release
Compatibility: novelyst v0.4.1 API 
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from pywriter.pywriter_globals import ERROR
from pywriter.config.configuration import Configuration
from pywriter.file.doc_open import open_document
from aeon2ywlib.json_timeline2 import JsonTimeline2
from aeon2ywlib.aeon2_converter import Aeon2Converter


class Aeon2Sync():
    """Plugin class for synchronization with Aeon Timeline 2.
    
    Public methods:
        disable_menu() -- disable menu entries when no project is open.
        enable_menu() -- enable menu entries when a project is open.
        
    """
    SETTINGS = dict(
        narrative_arc='Narrative',
        property_description='Description',
        property_notes='Notes',
        role_location='Location',
        role_item='Item',
        role_character='Participant',
        type_character='Character',
        type_location='Location',
        type_item='Item',
        color_scene='Red',
        color_event='Yellow',
    )
    OPTIONS = dict(
        scenes_only=True,
    )

    def __init__(self, ui):
        """Add a submenu to the main menu.
        
        Positional arguments:
            ui -- reference to the NovelystTk instance of the application.
        """
        self._exporter = Aeon2Converter
        self._ui = ui

        # Create a submenu
        self._aeon2Menu = tk.Menu(ui.mainMenu, title='my title', tearoff=0)
        ui.mainMenu.add_cascade(label='Aeon Timeline 2', menu=self._aeon2Menu)
        self._aeon2Menu.add_command(label='Information', underline=0, command=self._info)
        self._aeon2Menu.add_separator()
        self._aeon2Menu.add_command(label='Update timeline from yWriter', underline=7, command=self._yw2aeon)
        self._aeon2Menu.add_command(label='Update yWriter from timeline', underline=7, command=self._aeon2yw)
        self._aeon2Menu.add_separator()
        self._aeon2Menu.add_command(label='Edit timeline', underline=0, command=self._launch_aeon2)

    def disable_menu(self):
        """Disable menu entries when no project is open."""
        self._ui.mainMenu.entryconfig('Aeon Timeline 2', state='disabled')

    def enable_menu(self):
        """Enable menu entries when a project is open."""
        self._ui.mainMenu.entryconfig('Aeon Timeline 2', state='normal')

    def _launch_aeon2(self):
        """Launch Aeon Timeline 2 with the current project."""
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                if self._ui.lock():
                    open_document(timelinePath)
            else:
                self._ui.set_info_how(f'{ERROR}No Aeon Timeline 2 file available for this project.')

    def _yw2aeon(self):
        """Update timeline from yWriter.
        """
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                if self._ui.ask_yes_no('Save the project and update the timeline?'):
                    self._ui.save_project()
                    self._run(self._ui.ywPrj.filePath)
            else:
                self._ui.set_info_how(f'{ERROR}No Aeon Timeline 2 file available for this project.')

    def _info(self):
        """Show information about the Aeon Timeline 2 file."""
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                timestamp = os.path.getmtime(timelinePath)
                if timestamp > self._ui.ywPrj.timestamp:
                    cmp = 'newer'
                else:
                    cmp = 'older'
                fileDate = datetime.fromtimestamp(timestamp).replace(microsecond=0).isoformat(sep=' ')
                message = f'Aeon Timeline 2 file is {cmp} than the yWriter project.\n (last saved on {fileDate})'
            else:
                message = ('No Aeon Timeline 2 file available for this project.')
            messagebox.showinfo(self._ui.ywPrj.title, message)

    def _aeon2yw(self):
        """Update yWriter from timeline.
        """
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                if self._ui.ask_yes_no('Save the project and update from timeline?'):
                    self._ui.save_project()
                    self._run(timelinePath)
                    self._ui.reload_project()
            else:
                self._ui.set_info_how(f'{ERROR}No Aeon Timeline 2 file available for this project.')

    def _run(self, sourcePath):
        #--- Try to get persistent configuration data
        sourceDir = os.path.dirname(sourcePath)
        if not sourceDir:
            sourceDir = '.'
        try:
            homeDir = str(Path.home()).replace('\\', '/')
            installDir = f'{homeDir}/.pywriter/{self.APPNAME}/config'
        except:
            installDir = '.'
        iniFileName = 'aeon2yw.ini'
        iniFiles = [f'{installDir}/{iniFileName}', f'{sourceDir}/{iniFileName}']
        configuration = Configuration(self.SETTINGS, self.OPTIONS)
        for iniFile in iniFiles:
            configuration.read(iniFile)
        kwargs = {'suffix': ''}
        kwargs.update(configuration.settings)
        kwargs.update(configuration.options)
        converter = Aeon2Converter()
        converter.ui = self._ui
        converter.run(sourcePath, **kwargs)

