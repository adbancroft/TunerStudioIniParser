import sys
from TsIniParser import TsIniParser
from logging import DEBUG
from lark import logger
from TsIniParser import DataClassTransformer
import jsonpickle

logger.setLevel(DEBUG)

if __name__ == '__main__':
    parser = TsIniParser()
    parser.define('LAMBDA', True)
    parser.define('ALPHA_N', True)
    with open(sys.argv[1], 'r') as file:  
        tree = parser.parse(file)
        print(len(tree.children))
        dataclass = DataClassTransformer().transform(tree)

        injBatRates = dataclass['Constants'][6]['injBatRates']
        print(injBatRates.dim1d)