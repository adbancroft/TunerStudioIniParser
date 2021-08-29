from pathlib import Path

THIS_DIR = Path(__file__).parent

def parse_file(filepath, parser):
    with open(filepath, 'r', encoding='latin-1') as file:  
        return parser.parse(file)

def get_test_ini_path(relative_path):
    return THIS_DIR / relative_path