"""Aeon Timeline 2 sync plugin for novelyst.

Version @release
Compatibility: novelyst v0.6.0 API 
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

APPLICATION = 'Aeon Timeline 2'
PLUGIN = f'{APPLICATION} plugin v@release'
INI_FILENAME = 'aeon2yw.ini'
INI_FILEPATH = '.pywriter/aeon2yw/config'


class Plugin():
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
        add_moonphase=False,
    )

    def __init__(self, ui):
        """Add a submenu to the main menu.
        
        Positional arguments:
            ui -- reference to the NovelystTk instance of the application.
        """
        self._exporter = Aeon2Converter
        self._ui = ui

        # Create a submenu
        self._pluginMenu = tk.Menu(self._ui.mainMenu, title='my title', tearoff=0)
        self._ui.mainMenu.add_cascade(label=APPLICATION, menu=self._pluginMenu)
        self._ui.mainMenu.entryconfig(APPLICATION, state='disabled')
        self._pluginMenu.add_command(label='Information', underline=0, command=self._info)
        self._pluginMenu.add_separator()
        self._pluginMenu.add_command(label='Update timeline from yWriter', underline=7, command=self._export_from_yw)
        self._pluginMenu.add_command(label='Update yWriter from timeline', underline=7, command=self._import_to_yw)
        self._pluginMenu.add_separator()
        self._pluginMenu.add_command(label='Add or update moon phase data', underline=14, command=self._add_moonphase)
        self._pluginMenu.add_separator()
        self._pluginMenu.add_command(label='Edit timeline', underline=0, command=self._launch_application)

    def disable_menu(self):
        """Disable menu entries when no project is open."""
        self._ui.mainMenu.entryconfig(APPLICATION, state='disabled')

    def enable_menu(self):
        """Enable menu entries when a project is open."""
        self._ui.mainMenu.entryconfig(APPLICATION, state='normal')

    def _launch_application(self):
        """Launch Aeon Timeline 2 with the current project."""
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                if self._ui.lock():
                    open_document(timelinePath)
            else:
                self._ui.set_info_how(f'{ERROR}No {APPLICATION} file available for this project.')

    def _add_moonphase(self):
        """Add/update moon phase data.
        
        Add the moon phase to the event properties.
        If the moon phase event property already exists, just update.
        """
        #--- Try to get persistent configuration data
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                sourceDir = os.path.dirname(timelinePath)
                if not sourceDir:
                    sourceDir = '.'
                try:
                    homeDir = str(Path.home()).replace('\\', '/')
                    pluginCnfDir = f'{homeDir}/{INI_FILEPATH}'
                except:
                    pluginCnfDir = '.'
                iniFiles = [f'{pluginCnfDir}/{INI_FILENAME}', f'{sourceDir}/{INI_FILENAME}']
                configuration = Configuration(self.SETTINGS, self.OPTIONS)
                for iniFile in iniFiles:
                    configuration.read(iniFile)
                kwargs = {}
                kwargs.update(configuration.settings)
                kwargs.update(configuration.options)
                kwargs['add_moonphase'] = True
                timeline = JsonTimeline2(timelinePath, **kwargs)
                message = timeline.read()
                if message.startswith(ERROR):
                    self._ui.set_info_how(message)
                else:
                    self._ui.set_info_how(timeline.write())

    def _export_from_yw(self):
        """Update timeline from yWriter.
        """
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                if self._ui.ask_yes_no('Save the project and update the timeline?'):
                    self._ui.save_project()
                    self._run(self._ui.ywPrj.filePath)
            else:
                self._ui.set_info_how(f'{ERROR}No {APPLICATION} file available for this project.')

    def _info(self):
        """Show information about the Aeon Timeline 2 file."""
        if self._ui.ywPrj:
            timelinePath = f'{os.path.splitext(self._ui.ywPrj.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                try:
                    timestamp = os.path.getmtime(timelinePath)
                    if timestamp > self._ui.ywPrj.timestamp:
                        cmp = 'newer'
                    else:
                        cmp = 'older'
                    fileDate = datetime.fromtimestamp(timestamp).replace(microsecond=0).isoformat(sep=' ')
                    message = f'{APPLICATION} file is {cmp} than the yWriter project.\n (last saved on {fileDate})'
                except:
                    message = 'Cannot determine file date.'
            else:
                message = (f'No {APPLICATION} file available for this project.')
            messagebox.showinfo(PLUGIN, message)

    def _import_to_yw(self):
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
                self._ui.set_info_how(f'{ERROR}No {APPLICATION} file available for this project.')

    def _run(self, sourcePath):
        #--- Try to get persistent configuration data
        sourceDir = os.path.dirname(sourcePath)
        if not sourceDir:
            sourceDir = '.'
        try:
            homeDir = str(Path.home()).replace('\\', '/')
            pluginCnfDir = f'{homeDir}/{INI_FILEPATH}'
        except:
            pluginCnfDir = '.'
        iniFiles = [f'{pluginCnfDir}/{INI_FILENAME}', f'{sourceDir}/{INI_FILENAME}']
        configuration = Configuration(self.SETTINGS, self.OPTIONS)
        for iniFile in iniFiles:
            configuration.read(iniFile)
        kwargs = {'suffix': ''}
        kwargs.update(configuration.settings)
        kwargs.update(configuration.options)
        converter = Aeon2Converter()
        converter.ui = self._ui
        converter.run(sourcePath, **kwargs)

