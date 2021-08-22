import unittest
from logging import DEBUG, StreamHandler, getLogger
from TsIniParser import TsIniParser, TsParseTreeTransformer
from pathlib import Path

from lark import logger
logger.setLevel(DEBUG)

THIS_DIR = Path(__file__).parent

def parse_file(filepath, parser):
    with open(filepath, 'r', encoding='latin-1') as file:  
        return parser.parse(file)

class test_all_files(unittest.TestCase):

    def test_speeduino(self):
        parser = TsIniParser()
        test_file = THIS_DIR / "Test_Files" /  "speeduino.ini"
        tree = parse_file(test_file, parser)
        result = TsParseTreeTransformer().transform(tree)
        print(len(result))

    def test_allfiles(self):
        parser = TsIniParser()
        parser.define('LAMBDA', True)
        parser.define('ALPHA_N', True)

        exclude = [
                    'Trans00028.6.ini',
                    'Trans00028.7.ini',
                ]
        test_file_folder = THIS_DIR / "Test_Files"
        ini_files = (ini_file for ini_file in test_file_folder.glob("*.ini") if ini_file.name not in exclude)

        log = getLogger( "test_all_files.test_allfiles" )
        log.addHandler(StreamHandler())
        log.setLevel(DEBUG)

        for ini_file in ini_files:
            log.info(f"Parsing {ini_file}")
            parse_file(ini_file, parser)

if __name__ == '__main__':
    unittest.main()