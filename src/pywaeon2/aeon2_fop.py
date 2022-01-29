"""Provide helper functions for Aeon Timeline 2 file operation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import zipfile
import codecs
import json
import os


def open_timeline(filePath):
    """Unzip the project file and read 'timeline.json'.
    Return a message beginning with SUCCESS or ERROR
    and the JSON timeline structure.
    """

    try:
        with zipfile.ZipFile(filePath, 'r') as myzip:
            jsonBytes = myzip.read('timeline.json')
            jsonStr = codecs.decode(jsonBytes, encoding='utf-8')

    except:
        return 'ERROR: Cannot read JSON data.', None

    if not jsonStr:
        return 'ERROR: No JSON part found.', None

    try:
        jsonData = json.loads(jsonStr)

    except('JSONDecodeError'):
        return 'ERROR: Invalid JSON data.'
        None

    return 'SUCCESS', jsonData


def save_timeline(jsonData, filePath):
    """Write the jsonData structure to a zipfile located at filePath.
    Return a message beginning with SUCCESS or ERROR.
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

        return f'ERROR: Cannot write "{os.path.normpath(filePath)}".'

    return f'SUCCESS: "{os.path.normpath(filePath)}" written.'
