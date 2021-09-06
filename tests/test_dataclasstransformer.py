from pathlib import Path
import unittest
import sys
sys.path.insert(0, Path(__file__).parent.absolute())

from ts_ini_parser import *
try:
    from test_utils import parse_file, get_test_ini_path
except:
    from .test_utils import parse_file, get_test_ini_path


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

    def test_constants(self):
        section = self.subject['Constants']
        self.assertIsInstance(section, ConstantsSection)
        self.assertIsInstance(section, dict)
        self.assertEqual(14, len(section))

        page = section[7]
        self.assertIsInstance(page, Page)
        self.assertIsInstance(page, dict)
        self.assertEqual(9, len(page))

        table2d = page['vvtTable']
        self.assertIsInstance(table2d, Array2dVariable)
        self.assertIsInstance(table2d.dim2d, MatrixDimensions)        
        self.assertEqual('U08', table2d.data_type.type_name)

        bit_field = section[1]['aeMode']
        self.assertIsInstance(bit_field, BitVariable)
        self.assertIsInstance(bit_field.bit_size, BitSize)        
        self.assertEqual(4, len(bit_field.unknown_values))

    def test_tableeditor(self):
        section = self.subject['TableEditor']
        self.assertIsInstance(section, DictSection)
        self.assertIsInstance(section, dict)
        self.assertEqual(19, len(section))

        table = section['dwell_map']
        self.assertIsInstance(table, Table)
        self.assertSequenceEqual(table.xy_labels, ['RPM', 'Load: '])
        self.assertSequenceEqual(table.updown_labels, ['HIGHER', 'LOWER'])

        self.assertEqual(section['veTable1Tbl'].help_topic, 'http://speeduino.com/wiki/index.php/Tuning')
        self.assertEqual(section['veTable1Tbl'].grid_height, 2.0)
        self.assertSequenceEqual(section['veTable1Tbl'].grid_orient, [250, 0, 340])

    def test_curveeditor(self):
        section = self.subject['CurveEditor']
        self.assertIsInstance(section, DictSection)
        self.assertIsInstance(section, dict)
        self.assertEqual(31, len(section))

        curve = section['idle_advance_curve']
        self.assertIsInstance(curve, Curve)
        self.assertSequenceEqual(curve.column_labels, ['RPM Delta', 'Advance'])
        self.assertEqual(curve.curve_dimensions.xsize, 450)
        self.assertEqual(curve.curve_dimensions.ysize, 200)

        self.assertEqual(section['warmup_curve'].curve_gauge, 'cltGauge')
        self.assertSequenceEqual(section['warmup_analyzer_curve'].line_label, ['Current WUE', 'Recommended WUE'])

    def test_variablerefs_replacedinline(self):
        self.assertEqual(len(self.subject['PcVariables']['algorithmNames'].unknown_values), 8)
        self.assertEqual(len(self.subject['Constants'][13]['outputPin0'].unknown_values), 130)
        self.assertIsInstance(self.subject['Constants'][9]['caninput_sel0a'].unknown_values[4][1], Array1dVariable)

    def test_interline_references(self):
        self.assertIs(self.subject['Constants'][7]['rpmBinsBoost'], self.subject['TableEditor']['boostTbl'].xbins.constant_ref)
        self.assertEqual(self.subject['TableEditor']['boostTbl'].xbins.constant_ref.size, 8)
        self.assertIs(self.subject['Constants'][7]['tpsBinsBoost'], self.subject['TableEditor']['boostTbl'].ybins.constant_ref)
        self.assertIs(self.subject['Constants'][7]['boostTable'], self.subject['TableEditor']['boostTbl'].zbins.constant_ref)

        self.assertIs(self.subject['Constants'][4]['taeBins'], self.subject['CurveEditor']['time_accel_tpsdot_curve'].xbins.constant_ref)
        self.assertIs(self.subject['PcVariables']['wueAFR'], self.subject['CurveEditor']['warmup_afr_curve'].ybins.constant_ref)

    def test_datatype(self):
        data_type = self.subject['Constants'][1]['aseTaperTime'].data_type
        self.assertIsInstance(data_type, DataType)
        self.assertEqual('U08', data_type.type_name)
        self.assertEqual(1, data_type.width)

    def test_variable_size(self):
        self.assertEqual(self.subject['PcVariables']['wueAFR'].size, 20)
        self.assertEqual(self.subject['PcVariables']['algorithmLimits'].size, 16)
        self.assertEqual(self.subject['Constants'][2]['veTable'].size, 256)
        self.assertEqual(self.subject['Constants'][1]['vssPulsesPerKm'].size, 2)
        self.assertEqual(self.subject['Constants'][1]['vssMode'].size, 1)


if __name__ == '__main__':
    unittest.main()
