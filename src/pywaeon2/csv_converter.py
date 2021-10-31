"""Provide a csv converter class for yWriter projects. 

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.converter.new_project_factory import NewProjectFactory

from paeon.csv_timeline2 import CsvTimeline2
from paeon.json_timeline2 import JsonTimeline2


class CsvConverter(YwCnvUi):
    """A converter class for csv timeline import."""
    CREATE_SOURCE_CLASSES = [CsvTimeline2, JsonTimeline2]

    def __init__(self):
        YwCnvUi.__init__(self)
        self.newProjectFactory = NewProjectFactory(self.CREATE_SOURCE_CLASSES)