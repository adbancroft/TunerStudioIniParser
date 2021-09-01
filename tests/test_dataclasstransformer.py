import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from TsIniParser import TsIniParser, DataClassTransformer, Array1dVariable
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

    def test_speeduino(self):
        self.assertEqual(22, len(self.subject))
        self.assertEqual(14, len(self.subject['Constants']))
        self.assertEquals('U08', self.subject['Constants'][5]['afrTable'].data_type)

        # Code override check
        self.assertEqual(self.subject['Constants'][9]['caninput_sel0a'].unknown_values[4][0], 'code_override')
        self.assertIsInstance(self.subject['Constants'][9]['caninput_sel0a'].unknown_values[4][1], Array1dVariable)

        self.assertEqual(22, len(self.subject))
        self.assertEqual(14, len(self.subject['Constants']))
        self.assertEqual('U08', self.subject['Constants'][5]['afrTable'].data_type)

        # Check the inter section references were plumbed in
        self.assertEqual(self.subject['Constants'][7]['rpmBinsBoost'], self.subject['TableEditor']['boostTbl'].xbins.constant_ref)
        self.assertEqual(self.subject['Constants'][7]['tpsBinsBoost'], self.subject['TableEditor']['boostTbl'].ybins.constant_ref)
        self.assertEqual(self.subject['Constants'][7]['boostTable'], self.subject['TableEditor']['boostTbl'].zbins.constant_ref)

        self.assertEqual(self.subject['Constants'][4]['taeBins'], self.subject['CurveEditor']['time_accel_tpsdot_curve'].xbins.constant_ref)
        self.assertEqual(self.subject['PcVariables']['wueAFR'], self.subject['CurveEditor']['warmup_afr_curve'].ybins.constant_ref)

    def test_variablerefs_replacedinline(self):
        self.assertEqual(len(self.subject['PcVariables']['algorithmNames'].unknown_values), 8)
        self.assertEqual(len(self.subject['Constants'][13]['outputPin0'].unknown_values), 130)
        tree = parse_file(get_test_ini_path(Path("Test_Files") / "speeduino.ini"), parser)
        result = DataClassTransformer().transform(tree)
        self.assertEqual(22, len(result))
        self.assertEqual(14, len(result['Constants']))
        self.assertEqual('U08', result['Constants'][5]['afrTable'].data_type)

        # Check the inter section references were plumbed in
        self.assertEqual(result['Constants'][7]['rpmBinsBoost'], result['TableEditor']['boostTbl'].xbins.constant_ref)
        self.assertEqual(result['Constants'][7]['tpsBinsBoost'], result['TableEditor']['boostTbl'].ybins.constant_ref)
        self.assertEqual(result['Constants'][7]['boostTable'], result['TableEditor']['boostTbl'].zbins.constant_ref)

        self.assertEqual(result['Constants'][4]['taeBins'], result['CurveEditor']['time_accel_tpsdot_curve'].xbins.constant_ref)
        self.assertEqual(result['PcVariables']['wueAFR'], result['CurveEditor']['warmup_afr_curve'].ybins.constant_ref)


if __name__ == '__main__':
    unittest.main()
