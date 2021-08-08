import sys
from TsIniParser import TsIniParser

if __name__ == '__main__':
    parser = TsIniParser()
    parser.define('LAMBDA', True)
    parser.define('ALPHA_N', True)
    with open(sys.argv[1], 'r') as file:  
        tree = parser.parse(file)
        print(tree.pretty())