from pathlib import Path
from ts_ini_parser import TsIniParser, DataClassTransformer


parser = TsIniParser()
parser.define('LAMBDA', True)
parser.define('ALPHA_N', True)


test_file = Path(__file__).parent.joinpath('tests').joinpath('Test_Files').joinpath('speeduino.ini')
with test_file.open('r') as file:
    for run in range(3):
        file.seek(0)
        tree = parser.parse(file)
        print(len(tree.children))
        dataclass = DataClassTransformer().transform(tree)

        injBatRates = dataclass['Constants'][6]['injBatRates']
        print(injBatRates.dim1d)
