""" Python unit tests for the aeon2yw project.

Test suite for aeon2yw.pyw.

For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from shutil import copyfile
import os
import unittest
import aeon2yw

# Test environment

# The paths are relative to the "test" directory,
# where this script is placed and executed

TEST_PATH = os.getcwd() + '/../test'
TEST_DATA_PATH = TEST_PATH + '/data/'
TEST_EXEC_PATH = TEST_PATH + '/yw7/'

# To be placed in TEST_DATA_PATH:
NORMAL_AEON = TEST_DATA_PATH + 'normal.aeonzip'
NORMAL_YW7 = TEST_DATA_PATH + 'normal.yw7'
MINIMAL_AEON = TEST_DATA_PATH + 'minimal.aeonzip'
CREATED_AEON = TEST_DATA_PATH + 'created.aeonzip'

DATE_LIMITS_AEON = TEST_DATA_PATH + 'date_limits.aeonzip'
DATE_LIMITS_YW7 = TEST_DATA_PATH + 'date_limits.yw7'


SCENES_ONLY_INI = TEST_DATA_PATH + 'scenes_only.ini'
UPDATE_NOTES_INI = TEST_DATA_PATH + 'update_notes.ini'
UPDATED_AEON = TEST_DATA_PATH + 'updated.aeonzip'
UPDATED_YW7 = TEST_DATA_PATH + 'updated.yw7'

# Test data
INI_FILE = TEST_EXEC_PATH + 'aeon2yw.ini'
TEST_YW7 = TEST_EXEC_PATH + 'yw7 Sample Project.yw7'
TEST_YW7_BAK = TEST_EXEC_PATH + 'yw7 Sample Project.yw7.bak'
TEST_AEON = TEST_EXEC_PATH + 'yw7 Sample Project.aeonzip'


def read_file(inputFile):
    try:
        with open(inputFile, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        with open(inputFile, 'r') as f:
            return f.read()


def remove_all_testfiles():

    try:
        os.remove(TEST_YW7)

    except:
        pass

    try:
        os.remove(TEST_YW7_BAK)

    except:
        pass

    try:
        os.remove(TEST_AEON)
    except:
        pass

    try:
        os.remove(INI_FILE)
    except:
        pass


class NormalOperation(unittest.TestCase):
    """Test case: Normal operation."""

    def setUp(self):

        try:
            os.mkdir(TEST_EXEC_PATH)

        except:
            pass

        remove_all_testfiles()

    def test_aeon2_aeonzip(self):
        copyfile(NORMAL_AEON, TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw.run(TEST_AEON, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(NORMAL_YW7))

    def test_date_limits_aeonzip(self):
        copyfile(DATE_LIMITS_AEON, TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw.run(TEST_AEON, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(DATE_LIMITS_YW7))

    def test_update(self):
        copyfile(UPDATE_NOTES_INI, INI_FILE)
        copyfile(DATE_LIMITS_YW7, TEST_YW7)
        copyfile(UPDATED_AEON, TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw.run(TEST_AEON, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(UPDATED_YW7))

    @unittest.skip('cannot compare result because of random GUIDs')
    def test_create(self):
        copyfile(DATE_LIMITS_YW7, TEST_YW7)
        copyfile(MINIMAL_AEON, TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw.run(DATE_LIMITS_YW7, silentMode=True)
        #self.assertEqual(open_timeline(TEST_AEON)[1], open_timeline(CREATED_AEON)[1])

    def tearDown(self):
        remove_all_testfiles()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
