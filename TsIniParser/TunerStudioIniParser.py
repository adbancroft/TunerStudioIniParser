from .TunerStudioIniPreProcessor import TsIniPreProcessor
from .TreeLexer import TreeLexerAdapter
from lark import Lark, Tree
from pathlib import Path

_GRAMMAR = Path(__file__).parent / 'ts_ini.lark'
_GRAMMAR_CACHE = _GRAMMAR.with_suffix('.lark.cache')

class TsIniParser:
    """TunerStudio INI file parser
    
    This parser is slightly less tolerant than TunerStudio:
     key-value pairs: the values must be comma delimited (TunerStudio tolerates spaces)
     there must be a blank line at the end
     Expression markers ("{", "}") and parentheses must be balanced
     All identifiers must be cnames (no spaces, quotes etc.)
    """

    def __init__(self):
        self._pre_processor = TsIniPreProcessor()
        self._ts_parser = Lark.open(_GRAMMAR, parser='lalr', debug = True, cache = str(_GRAMMAR_CACHE))
        # Adapt the parser lexer to consume the preprocessor output (a Tree)
        self._ts_parser.parser.lexer = TreeLexerAdapter(self._ts_parser.parser.lexer)

    def define(self, symbol:str, value):
        """Define a preprocessor symbol to control preprocessing condtionals

        Equivalent of #set in the INI file. E.g.
          #set CAN_COMMANDS
        becomes
          define('CAN_COMMANDS', True)
        """
        
        self._pre_processor.define(symbol, value)

    def parse(self, input, on_error=None) -> Tree:
        return self._ts_parser.parse(self._pre_processor.pre_process(input, on_error=on_error), on_error=on_error)