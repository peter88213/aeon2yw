"""Aeon Timeline 2 sync plugin for novelyst.

Version @release
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pathlib import Path
import tkinter as tk
from pywriter.config.configuration import Configuration
from aeon2ywlib.aeon2_converter import Aeon2Converter


class Aeon2Sync():
    """Plugin for synchronization with Aeon Timeline 2.
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

    def __init__(self, app):
        """Add a submenu to the main menu.
        
        Positional arguments:
            app -- reference to the NovelystTk instance.
        """
        self._exporter = Aeon2Converter
        self.app = app

        # Create a submenu
        self._aeon2Menu = tk.Menu(app.mainMenu, title='my title', tearoff=0)
        app.mainMenu.add_cascade(label='Aeon Timeline 2', menu=self._aeon2Menu)
        self._aeon2Menu.add_command(label='Synchronize', underline=0, command=self._run)

    def _run(self):
        #--- Try to get persistent configuration data
        sourceDir = os.path.dirname(self.app.ywPrj.filePath)
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
        converter.ui = self.app
        converter.run(self.app.ywPrj.filePath, **kwargs)

