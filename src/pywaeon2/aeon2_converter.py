"""Provide a converter class for Aeon Timeline 2 and yWriter. 

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.pywriter_globals import ERROR
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File

from pywaeon2.json_timeline2 import JsonTimeline2
from pywaeon2.yw7_sync import Yw7Sync


class Aeon2Converter(YwCnvUi):
    """A converter class for yWriter and Aeon Timeline 2."""

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.
        """
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'{ERROR}File "{os.path.normpath(sourcePath)}" not found.')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == JsonTimeline2.EXTENSION:
            sourceFile = JsonTimeline2(sourcePath, **kwargs)

            if os.path.isfile(f'{fileName}{Yw7File.EXTENSION}'):
                targetFile = Yw7Sync(f'{fileName}{Yw7Sync.EXTENSION}', **kwargs)
                sourceFile.ywProject = targetFile
                self.import_to_yw(sourceFile, targetFile)

            else:
                targetFile = Yw7File(f'{fileName}{Yw7File.EXTENSION}', **kwargs)
                self.create_yw7(sourceFile, targetFile)

        elif fileExtension == Yw7File.EXTENSION:
            sourceFile = Yw7File(sourcePath, **kwargs)
            targetFile = JsonTimeline2(f'{fileName}{JsonTimeline2.EXTENSION}', **kwargs)
            self.export_from_yw(sourceFile, targetFile)

        else:
            self.ui.set_info_how(f'{ERROR}File type of "{os.path.normpath(sourcePath)}" not supported.')
            return
