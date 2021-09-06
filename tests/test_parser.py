import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from logging import DEBUG, StreamHandler, getLogger
from ts_ini_parser import TsIniParser
try:
    from test_utils import parse_file, get_test_ini_path
except:
    from .test_utils import parse_file, get_test_ini_path
from pathlib import Path

from lark import logger
logger.setLevel(DEBUG)


class test_parser(unittest.TestCase):

    def test_speeduino(self):
        # This is a quick test
        parser = TsIniParser()
        tree = parse_file(get_test_ini_path(Path("Test_Files") / "speeduino.ini"), parser)
        self.assertIsNotNone(tree)
        self.assertEqual(2, len(tree.children))
        self.assertEqual(22, len(tree.children[1].children))

    def test_allfiles_noexceptions(self):
        # Test all known INI files
        parser = TsIniParser(ignore_hash_error=True)

        test_file_folder = get_test_ini_path('Test_Files')
        ini_files = test_file_folder.glob("*.ini")

        log = getLogger(self.__class__.__name__)
        log.addHandler(StreamHandler())
        log.setLevel(DEBUG)

        try:
            for ini_file in ini_files:
                log.info(f"Parsing {ini_file}")
                self.assertIsNotNone(parse_file(ini_file, parser))
        except Exception as error:
            self.fail(f"Failed with {str(error)}")


if __name__ == '__main__':
    unittest.main()
