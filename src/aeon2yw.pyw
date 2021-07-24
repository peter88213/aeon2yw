#!/usr/bin/env python3
"""Aeon Timeline 2 csv to yWriter converter 

Version @release
Requires Python 3.7 or above

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/Paeon
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse

from pywriter.ui.ui import Ui
from pywriter.ui.ui_tk import UiTk
from pywaeon.csv.csv_converter import CsvConverter

SUFFIX = ''


def run(sourcePath, silentMode=True):

    if silentMode:
        ui = Ui('')

    else:
        ui = UiTk('csv timeline to yWriter converter @release')

    kwargs = dict(
        suffix=SUFFIX,
        exportAllEvents=True,
        sceneMarker='Scene',
        titleLabel='Title',
        sceneLabel='Tags',
        dateTimeLabel='Start Date',
        descriptionLabel='Description',
        notesLabel='Notes',
        tagLabel='Story',
        locationLabel='Location',
        itemLabel='Item',
        characterLabel='Participant',
    )
    converter = CsvConverter()
    converter.ui = ui
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Aeon Timeline 2 csv to yWriter converter',
        epilog='')
    parser.add_argument('sourcePath', metavar='Sourcefile',
                        help='The path of the csv timeline file.')

    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()

    if args.silent:
        silentMode = True

    else:
        silentMode = False

    run(args.sourcePath, silentMode)
