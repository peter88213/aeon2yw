""" Python unit tests for the aeon2yw project.

Test suite for aeon2yw.pyw.

For further information see https://github.com/peter88213/aeon2yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from shutil import copyfile
import os
import unittest
import sys
from io import StringIO
import zipfile
import codecs
import json
import aeon2yw_

# Test environment

# The paths are relative to the "test" directory,
# where this script is placed and executed

TEST_PATH = os.getcwd() + '/../test'
TEST_DATA_PATH = TEST_PATH + '/data/'
TEST_EXEC_PATH = TEST_PATH + '/yw7/'

# Test data
INI_FILE = TEST_EXEC_PATH + 'aeon2yw.ini'
TEST_YW7 = TEST_EXEC_PATH + 'yw7 Sample Project.yw7'
TEST_YW7_BAK = TEST_EXEC_PATH + 'yw7 Sample Project.yw7.bak'
TEST_AEON = TEST_EXEC_PATH + 'yw7 Sample Project.aeonzip'
TEST_AEON_BAK = TEST_EXEC_PATH + 'yw7 Sample Project.aeonzip.bak'


def open_timeline(filePath):
    """Unzip the project file and read 'timeline.json'.
    Return the JSON timeline structure.
    """
    try:
        with zipfile.ZipFile(filePath, 'r') as myzip:
            jsonBytes = myzip.read('timeline.json')
            jsonStr = codecs.decode(jsonBytes, encoding='utf-8')
    except:
        raise Error(f'Cannot read JSON data.')

    if not jsonStr:
        raise Error(f'No JSON part found.')

    try:
        jsonData = json.loads(jsonStr)
    except('JSONDecodeError'):
        raise Error(f'Invalid JSON data.')

    return jsonData


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
        os.remove(TEST_AEON_BAK)
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
        self.test_out = StringIO()
        self.test_err = StringIO()
        self.original_output = sys.stdout
        self.original_err = sys.stderr
        sys.stdout = self.test_out
        sys.stderr = self.test_err
        try:
            os.mkdir(TEST_EXEC_PATH)
        except:
            pass
        remove_all_testfiles()

    def test_ambiguous_aeon_event(self):
        copyfile(TEST_DATA_PATH + 'update_notes.ini', INI_FILE)
        copyfile(TEST_DATA_PATH + 'normal.aeonzip', TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw_.run(TEST_AEON, silentMode=True)
        self.assertStderrEquals('FAIL: Ambiguous Aeon event title "Mrs Hubbard sleeps".')

    def test_create_yw7(self):
        copyfile(TEST_DATA_PATH + 'update_notes.ini', INI_FILE)
        copyfile(TEST_DATA_PATH + 'date_limits.aeonzip', TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw_.run(TEST_AEON, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(TEST_DATA_PATH + 'date_limits_notes.yw7'))

    def test_create_yw7_narrative_only(self):
        copyfile(TEST_DATA_PATH + 'narrative_only.ini', INI_FILE)
        copyfile(TEST_DATA_PATH + 'date_limits.aeonzip', TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw_.run(TEST_AEON, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(TEST_DATA_PATH + 'date_limits.yw7'))

    def test_update_yw7(self):
        copyfile(TEST_DATA_PATH + 'update_notes.ini', INI_FILE)
        copyfile(TEST_DATA_PATH + 'date_limits.yw7', TEST_YW7)
        copyfile(TEST_DATA_PATH + 'updated.aeonzip', TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw_.run(TEST_AEON, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(TEST_DATA_PATH + 'updated_notes.yw7'))
        self.assertEqual(read_file(TEST_YW7_BAK), read_file(TEST_DATA_PATH + 'date_limits.yw7'))

    def test_update_yw7_narrative_only(self):
        copyfile(TEST_DATA_PATH + 'narrative_only.ini', INI_FILE)
        copyfile(TEST_DATA_PATH + 'date_limits.yw7', TEST_YW7)
        copyfile(TEST_DATA_PATH + 'updated.aeonzip', TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw_.run(TEST_AEON, silentMode=True)
        self.assertEqual(read_file(TEST_YW7), read_file(TEST_DATA_PATH + 'updated.yw7'))
        self.assertEqual(read_file(TEST_YW7_BAK), read_file(TEST_DATA_PATH + 'date_limits.yw7'))

    def test_create_date_limits_aeon(self):
        copyfile(TEST_DATA_PATH + 'date_limits.yw7', TEST_YW7)
        copyfile(TEST_DATA_PATH + 'minimal.aeonzip', TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw_.run(TEST_YW7, silentMode=True)
        self.assertEqual(open_timeline(TEST_AEON), open_timeline(TEST_DATA_PATH + 'created.aeonzip'))

    def test_create_arc_aeon(self):
        copyfile(TEST_DATA_PATH + 'arc.yw7', TEST_YW7)
        copyfile(TEST_DATA_PATH + 'minimal.aeonzip', TEST_AEON)
        os.chdir(TEST_EXEC_PATH)
        aeon2yw_.run(TEST_YW7, silentMode=True)
        self.assertEqual(open_timeline(TEST_AEON), open_timeline(TEST_DATA_PATH + 'created_arc.aeonzip'))

    def tearDown(self):
        sys.stdout = self.original_output
        sys.stderr = self.original_err
        remove_all_testfiles()

    # assert that sys.stdout would be equal to expected value
    def assertStdoutEquals(self, value):
        self.assertEqual(self.test_out.getvalue().strip(), value)

    # assert that sys.stdout would not be equal to expected value
    def assertStdoutNotEquals(self, value):
        self.assertNotEqual(self.test_out.getvalue().strip(), value)

    # assert that sys.stderr would be equal to expected value
    def assertStderrEquals(self, value):
        self.assertEqual(self.test_err.getvalue().strip(), value)

    # assert that sys.stderr would not be equal to expected value
    def assertStderrNotEquals(self, value):
        self.assertNotEqual(self.test_err.getvalue().strip(), value)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
