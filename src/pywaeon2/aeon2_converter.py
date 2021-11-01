"""Provide a csv converter class for yWriter projects. 

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.converter.new_project_factory import NewProjectFactory

from paeon.csv_timeline2 import CsvTimeline2
from paeon.json_timeline2 import JsonTimeline2
from pywaeon2.yw7_sync_dt import Yw7SyncDt


class Aeon2Converter(YwCnvUi):
    """A converter class for yWriter and Aeon Timeline 2."""

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.
        Override the superclass method.
        """
        self.newFile = None

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how('ERROR: File "' + os.path.normpath(sourcePath) + '" not found.')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == Yw7SyncDt.EXTENSION:
            sourceFile = Yw7SyncDt(sourcePath, **kwargs)
            targetFile = JsonTimeline2(fileName + JsonTimeline2.EXTENSION, **kwargs)
            targetFile.back_up()
            targetFile.ywProject = sourceFile
            self.export_from_yw(sourceFile, targetFile)

        elif fileExtension == JsonTimeline2.EXTENSION:
            sourceFile = JsonTimeline2(sourcePath, **kwargs)
            targetFile = Yw7SyncDt(fileName + Yw7SyncDt.EXTENSION, **kwargs)

            if targetFile.file_exists():
                sourceFile.ywProject = targetFile
                targetFile.back_up()
                self.import_to_yw(sourceFile, targetFile)

            else:
                self.create_yw7(sourceFile, targetFile)

        else:
            self.ui.set_info_how('ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.')
