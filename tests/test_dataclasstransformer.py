import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
import more_itertools
from TsIniParser import *
try:
    from test_utils import parse_file, get_test_ini_path
except:
    from .test_utils import parse_file, get_test_ini_path
from pathlib import Path


class test_dataclasstransformer(unittest.TestCase):

    def setUp(self):
        parser = TsIniParser()
        path = Path("Test_Files") / "speeduino.ini"
        tree = parse_file(get_test_ini_path(path), parser)
        self.subject = DataClassTransformer().transform(tree)

    def test_basic(self):
        self.assertIsInstance(self.subject, TsIniFile)
        self.assertIsInstance(self.subject, dict)
        self.assertEqual(22, len(self.subject))

        section = self.subject['Constants']
        self.assertIsInstance(section, AbstractSection)
        self.assertIsInstance(section, dict)
        self.assertEqual(14, len(section))

        page = section[7]
        self.assertIsInstance(page, Page)
        self.assertIsInstance(page, dict)
        self.assertEqual(9, len(page))

        table2d = page['vvtTable']
        self.assertIsInstance(table2d, TableArray2dVariable)

        # Test a few types
        self.assertEquals('U08', self.subject['Constants'][5]['afrTable'].data_type)


    def test_variablerefs_replacedinline(self):
        self.assertEqual(len(self.subject['PcVariables']['algorithmNames'].unknown_values), 8)
        self.assertEqual(len(self.subject['Constants'][13]['outputPin0'].unknown_values), 130)
        self.assertIsInstance(self.subject['Constants'][9]['caninput_sel0a'].unknown_values[4][1], Array1dVariable)

    def test_interline_references(self):
        self.assertIsInstance(self.subject['Constants'][7]['rpmBinsBoost'], TableArray1dVariable)
        self.assertIs(self.subject['Constants'][7]['rpmBinsBoost'], self.subject['TableEditor']['boostTbl'].xbins.constant_ref)
        self.assertIsInstance(self.subject['Constants'][7]['tpsBinsBoost'], TableArray1dVariable)
        self.assertIs(self.subject['Constants'][7]['tpsBinsBoost'], self.subject['TableEditor']['boostTbl'].ybins.constant_ref)
        self.assertIsInstance(self.subject['Constants'][7]['boostTable'], TableArray2dVariable)
        self.assertIs(self.subject['Constants'][7]['boostTable'], self.subject['TableEditor']['boostTbl'].zbins.constant_ref)

        self.assertIsInstance(self.subject['Constants'][4]['taeBins'], CurveArray1dVariable)
        self.assertIs(self.subject['Constants'][4]['taeBins'], self.subject['CurveEditor']['time_accel_tpsdot_curve'].xbins.constant_ref)
        self.assertIsInstance(self.subject['PcVariables']['wueAFR'], CurveArray1dVariable)
        self.assertIs(self.subject['PcVariables']['wueAFR'], self.subject['CurveEditor']['warmup_afr_curve'].ybins.constant_ref)

if __name__ == '__main__':
    unittest.main()
