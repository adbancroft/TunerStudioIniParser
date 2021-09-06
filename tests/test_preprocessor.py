import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from ts_ini_parser import TsIniParser
try:
    from test_utils import parse_file, get_test_ini_path
except:
    from .test_utils import parse_file, get_test_ini_path
from pathlib import Path


class test_parser(unittest.TestCase):

    def test_hasherror_throws(self):
        parser = TsIniParser()
        parser.define('AIR_FLOW_METER', True)
        ini_file = get_test_ini_path(Path("Test_Files") / "megasquirt-I_B&G_2.0-3.0.ini")
        test_func = lambda: parse_file(ini_file, parser)
        self.assertRaises(SyntaxError, test_func)
