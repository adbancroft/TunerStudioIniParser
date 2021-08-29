import unittest
from TsIniParser import TsIniParser, DataClassTransformer
import test_utils
from pathlib import Path

class test_dataclasstransformer(unittest.TestCase):

    def test_speeduino(self):
        parser = TsIniParser()
        tree = test_utils.parse_file(test_utils.get_test_ini_path(Path("Test_Files") /  "speeduino.ini"), parser)
        result = DataClassTransformer().transform(tree)
        self.assertEqual(22, len(result))
        self.assertEqual(14, len(result['Constants']))
        self.assertEquals('U08', result['Constants'][5]['afrTable'].data_type)

        # Check the inter section references were plumbed in
        self.assertEqual(result['Constants'][7]['rpmBinsBoost'], result['TableEditor']['boostTbl'].xbins.constant_ref)
        self.assertEqual(result['Constants'][7]['tpsBinsBoost'], result['TableEditor']['boostTbl'].ybins.constant_ref)
        self.assertEqual(result['Constants'][7]['boostTable'], result['TableEditor']['boostTbl'].zbins.constant_ref)
        
        self.assertEqual(result['Constants'][4]['taeBins'], result['CurveEditor']['time_accel_tpsdot_curve'].xbins.constant_ref)
        self.assertEqual(result['PcVariables']['wueAFR'], result['CurveEditor']['warmup_afr_curve'].ybins.constant_ref)