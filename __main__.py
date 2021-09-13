from logging import DEBUG
from lark import logger
logger.setLevel(DEBUG)

if __name__ == '__main__':

    from ts_ini_parser import TsIniParser, DataClassTransformer
    import sys

    parser = TsIniParser(ignore_hash_error=True)
    parser.define('LAMBDA', True)
    parser.define('ALPHA_N', True)
    parser.define('INI_VERSION_2', True)
    parser.define('NARROW_BAND_EGO', True)
    with open(sys.argv[1], 'r') as file:
        tree = parser.parse(file)
        print(len(tree.children))
        dataclass = DataClassTransformer().transform(tree)

        mtVersion = dataclass['MegaTune'][0]
        print(mtVersion.values[0][1])
