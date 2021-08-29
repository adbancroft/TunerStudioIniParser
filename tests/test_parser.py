import unittest
from logging import DEBUG, StreamHandler, getLogger
from TsIniParser import TsIniParser, DataClassTransformer
import test_utils
from pathlib import Path

from lark import logger
logger.setLevel(DEBUG)

class test_parser(unittest.TestCase):

    def test_speeduino(self):
        # This is a quick test
        parser = TsIniParser()
        tree = test_utils.parse_file(test_utils.get_test_ini_path(Path("Test_Files") /  "speeduino.ini"), parser)
        self.assertIsNotNone(tree)
        self.assertEqual(2, len(tree.children))
        self.assertEqual(22, tree.children[1].children)

    def test_allfiles_noexceptions(self):
        # Test all known INI files
        parser = TsIniParser()
        parser.define('LAMBDA', True)
        parser.define('ALPHA_N', True)

        test_file_folder = test_utils.get_test_ini_path('Test_Files')
        ini_files = test_file_folder.glob("*.ini")
        
        log = getLogger(self.__class__.__name__)
        log.addHandler(StreamHandler())
        log.setLevel(DEBUG)

        try:
            for ini_file in ini_files:
                log.info(f"Parsing {ini_file}")
                self.assertIsNotNone(test_utils.parse_file(ini_file, parser))
        except Exception as error:
            self.fail(f"Failed with {str(error)}")

if __name__ == '__main__':
    unittest.main()