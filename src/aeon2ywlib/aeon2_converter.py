"""Provide a converter class for Aeon Timeline 2 and yWriter. 

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import *
from pywriter.yw.yw7_file import Yw7File
from pywriter.converter.yw_cnv_ui import YwCnvUi
from aeon2ywlib.json_timeline2 import JsonTimeline2


class Aeon2Converter(YwCnvUi):
    """A converter class for yWriter and Aeon Timeline 2.
    
    Public methods:
        run(sourcePath, **kwargs) -- Create source and target objects and run conversion.
    """

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath: str -- the source file path.
        
        The direction of the conversion is determined by the source file type.
        Only yWriter project files and Aeon Timeline 2 files are accepted.
        """
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'!{_("File not found")}: "{norm_path(sourcePath)}".')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)
        if fileExtension == JsonTimeline2.EXTENSION:
            # Source is a timeline
            sourceFile = JsonTimeline2(sourcePath, **kwargs)
            if os.path.isfile(f'{fileName}{Yw7File.EXTENSION}'):
                # Update existing yWriter project from timeline
                targetFile = Yw7File(f'{fileName}{Yw7File.EXTENSION}', **kwargs)
                self.import_to_yw(sourceFile, targetFile)
            else:
                # Create new yWriter project from timeline
                targetFile = Yw7File(f'{fileName}{Yw7File.EXTENSION}', **kwargs)
                self.create_yw7(sourceFile, targetFile)
        elif fileExtension == Yw7File.EXTENSION:
            # Update existing timeline from yWriter project
            sourceFile = Yw7File(sourcePath, **kwargs)
            targetFile = JsonTimeline2(f'{fileName}{JsonTimeline2.EXTENSION}', **kwargs)
            self.export_from_yw(sourceFile, targetFile)
        else:
            # Source file format is not supported
            self.ui.set_info_how(f'!{_("File type is not supported")}: "{norm_path(sourcePath)}".')
