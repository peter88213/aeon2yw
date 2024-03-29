"""Synchronize Aeon Timeline 2 and yWriter

Version @release
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import argparse
from pathlib import Path
from pywriter.pywriter_globals import *
from pywriter.ui.ui import Ui
from pywriter.ui.ui_tk import UiTk
from pywriter.ui.set_icon_tk import *
from pywriter.config.configuration import Configuration
from aeon2ywlib.aeon2_converter import Aeon2Converter

SUFFIX = ''
APPNAME = 'aeon2yw'
SETTINGS = dict(
    default_date_time='2023-01-01 00:00:00',
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
    color_point='Blue',
)
OPTIONS = dict(
    scenes_only=True,
    add_moonphase=False,
)


def run(sourcePath, silentMode=True, installDir='.'):
    if silentMode:
        ui = Ui('')
    else:
        ui = UiTk(f'{_("Synchronize Aeon Timeline 2 and yWriter")} @release')
        set_icon(ui.root, icon='aLogo32')

    #--- Try to get persistent configuration data
    sourceDir = os.path.dirname(sourcePath)
    if not sourceDir:
        sourceDir = '.'
    iniFileName = f'{APPNAME}.ini'
    iniFiles = [f'{installDir}/{iniFileName}', f'{sourceDir}/{iniFileName}']
    configuration = Configuration(SETTINGS, OPTIONS)
    for iniFile in iniFiles:
        configuration.read(iniFile)
    kwargs = {'suffix': SUFFIX}
    kwargs.update(configuration.settings)
    kwargs.update(configuration.options)
    converter = Aeon2Converter()
    converter.ui = ui

    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Synchronize Aeon Timeline 2 and yWriter',
        epilog='')
    parser.add_argument('sourcePath',
                        metavar='Sourcefile',
                        help='The path of the aeonzip or yw7 file.')

    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()
    try:
        homeDir = str(Path.home()).replace('\\', '/')
        installDir = f'{homeDir}/.pywriter/{APPNAME}/config'
    except:
        installDir = '.'
    run(args.sourcePath, args.silent, installDir)
