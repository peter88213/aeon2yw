"""Provide a csv converter class for yWriter projects. 

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw7_file import Yw7File
from paeon.csv_timeline2 import CsvTimeline2
from paeon.json_timeline2 import JsonTimeline2
from pywaeon2.yw7_sync import Yw7Sync


class Aeon2Converter(YwCnvUi):
    """A converter class for yWriter and Aeon Timeline 2."""

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.
        Override the superclass method.
        """
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how('ERROR: File "' + os.path.normpath(sourcePath) + '" not found.')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == JsonTimeline2.EXTENSION:
            sourceFile = JsonTimeline2(sourcePath, **kwargs)

        elif fileExtension == CsvTimeline2.EXTENSION:
            sourceFile = CsvTimeline2(sourcePath, **kwargs)

        else:
            self.ui.set_info_how('ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.')
            return

        if os.path.isfile(fileName + Yw7File.EXTENSION):
            targetFile = Yw7Sync(fileName + Yw7Sync.EXTENSION, **kwargs)
            sourceFile.ywProject = targetFile
            targetFile.back_up()
            self.import_to_yw(sourceFile, targetFile)

        else:
            targetFile = Yw7File(fileName + Yw7File.EXTENSION, **kwargs)
            self.create_yw7(sourceFile, targetFile)
