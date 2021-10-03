from pathlib import Path
import unittest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from ts_ini_parser import *
try:
    from test_utils import parse_file, get_test_ini_path
except:
    from .test_utils import parse_file, get_test_ini_path

from lark import logger
from logging import DEBUG, StreamHandler, getLogger

logger.setLevel(DEBUG)


class test_dataclasstransformer(unittest.TestCase):

    def setUp(self):
        parser = TsIniParser()
        path = Path("Test_Files") / "speeduino.ini"
        tree = parse_file(get_test_ini_path(path), parser)
        self.subject = DataClassTransformer().transform(tree)

    def test_basic(self):
        self.assertIsInstance(self.subject, TsIniFile)
        self.assertIsInstance(self.subject, UserDict)
        self.assertEqual(22, len(self.subject))

        self.assertEqual('iniSpecVersion', self.subject['TunerStudio'][0].name)

    def test_constants(self):
        section = self.subject['Constants']
        self.assertIsInstance(section, ConstantsSection)
        self.assertIsInstance(section, UserDict)
        self.assertEqual(14, len(section))

        page = section[7]
        self.assertIsInstance(page, Page)
        self.assertIsInstance(page, UserDict)
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
        self.assertIsInstance(section, UserDict)
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
        self.assertIsInstance(section, UserDict)
        self.assertEqual(31, len(section))

        curve = section['idle_advance_curve']
        self.assertIsInstance(curve, Curve)
        self.assertSequenceEqual(curve.lines[0].column_label, 'RPM Delta')
        self.assertEqual(curve.curve_dimensions.xsize, 450)
        self.assertEqual(curve.curve_dimensions.ysize, 200)

        self.assertEqual(section['warmup_curve'].curve_gauge, 'cltGauge')
        self.assertSequenceEqual(section['warmup_analyzer_curve'].lines[0].line_label, 'Current WUE')

    def test_variablerefs_replacedinline(self):
        self.assertEqual(len(self.subject['PcVariables']['algorithmNames'].unknown_values), 8)
        self.assertEqual(len(self.subject['Constants'][13]['outputPin0'].unknown_values), 130)
        self.assertIsInstance(self.subject['Constants'][9]['caninput_sel0a'].unknown_values[4][1], Array1dVariable)

    def test_interline_references(self):
        self.assertIs(self.subject['Constants'][7]['rpmBinsBoost'], self.subject['TableEditor']['boostTbl'].table_xbin.variable)
        self.assertEqual(self.subject['TableEditor']['boostTbl'].table_ybin.variable.size, 8)
        self.assertIs(self.subject['Constants'][7]['tpsBinsBoost'], self.subject['TableEditor']['boostTbl'].table_ybin.variable)
        self.assertIs(self.subject['Constants'][7]['boostTable'], self.subject['TableEditor']['boostTbl'].zbins.variable)

        self.assertIs(self.subject['Constants'][4]['taeBins'], self.subject['CurveEditor']['time_accel_tpsdot_curve'].lines[0].xbin.variable)
        self.assertIs(self.subject['PcVariables']['wueAFR'], self.subject['CurveEditor']['warmup_afr_curve'].lines[0].ybin.variable)

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

    @unittest.skip("Not sure about always running this yet - it's slow")
    def test_all_ini(self):
        # Test all known INI files
        parser = TsIniParser(ignore_hash_error=True)
        parser.define('LAMBDA', True)
        parser.define('ALPHA_N', True)
        parser.define('INI_VERSION_2', True)
        parser.define('NARROW_BAND_EGO', True)

        test_file_folder = get_test_ini_path('Test_Files')
        ini_files = test_file_folder.glob("*.ini")

        log = getLogger(self.__class__.__name__)
        log.addHandler(StreamHandler())
        log.setLevel(DEBUG)

        # Files we can't transform....yet
        exclude_ini = [
            'MS2ExtraSerial321.ini',
            'MS2ExtraSerial323.ini',
            'MS2ExtraSerial324.ini',
            'MS2ExtraSerial325.ini',
        ]

        for ini_file in ini_files:
            if ini_file.name not in exclude_ini:
                log.info(f"Parsing {ini_file}")
                try:
                    tree = parse_file(ini_file, parser)
                    self.assertIsNotNone(tree)
                    dataclass = DataClassTransformer().transform(tree)
                    self.assertIsNotNone(dataclass)
                except Exception as error:
                    msg = f'{ini_file} failed with {str(error)}'
                    self.fail(msg)


if __name__ == '__main__':
    unittest.main()
