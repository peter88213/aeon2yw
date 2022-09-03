"""Provide helper functions for Aeon Timeline 2 file operation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import zipfile
import codecs
import json
import os
from pywriter.pywriter_globals import *


def open_timeline(filePath):
    """Unzip the project file and read 'timeline.json'.

    Positional arguments:
        filePath -- Path of the .aeon project file to read.
        
    Return a message beginning with the ERROR constant in case of error
    and a Python object containing the timeline structure.
    """
    try:
        with zipfile.ZipFile(filePath, 'r') as myzip:
            jsonBytes = myzip.read('timeline.json')
            jsonStr = codecs.decode(jsonBytes, encoding='utf-8')
    except:
        return f'{ERROR}{_("Cannot read timeline data")}.', None
    if not jsonStr:
        return f'{ERROR}{_("No JSON part found in timeline data")}.', None
    try:
        jsonData = json.loads(jsonStr)
    except('JSONDecodeError'):
        return f'{ERROR}{_("Invalid JSON data in timeline")}.'
        None
    return 'Timeline data read in.', jsonData


def save_timeline(jsonData, filePath):
    """Write the timeline to a zipfile located at filePath.
    
    Positional arguments:
        jsonData -- Python object containing the timeline structure.
        filePath -- Path of the .aeon project file to write.
        
    Return a message beginning with the ERROR constant in case of error.
    """
    if os.path.isfile(filePath):
        os.replace(filePath, f'{filePath}.bak')
        backedUp = True
    else:
        backedUp = False
    try:
        with zipfile.ZipFile(filePath, 'w', compression=zipfile.ZIP_DEFLATED) as f:
            f.writestr('timeline.json', json.dumps(jsonData))
    except:
        if backedUp:
            os.replace(f'{filePath}.bak', filePath)
        return f'{ERROR}{_("Cannot write file")}: "{os.path.normpath(filePath)}".'

    return f'"{os.path.normpath(filePath)}" written.'
