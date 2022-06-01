"""Provide a class for a yWriter7 project to provide updates to Aeon Timeline 2.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.yw.yw7_file import Yw7File


class Yw7Source(Yw7File):
    """yWriter 7 project file representation.
    Extend the superclass
    """
    _SCN_KWVAR = (
        'Field_SceneArcs',
        )

