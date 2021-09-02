from pathlib import Path
from lark import Lark, Tree, Transformer
from .ts_ini_preprocessor import TsIniPreProcessor
from .tree_lexer import TreeLexerAdapter

_GRAMMAR = Path(__file__).parent / 'grammars' / 'ts_ini.lark'
_GRAMMAR_CACHE = _GRAMMAR.with_suffix('.lark.cache')


class TsIniParser:
    """TunerStudio INI file parser

    This parser is slightly less tolerant than TunerStudio:
     key-value pairs: the values must be comma delimited
        (TunerStudio tolerates spaces)
     there must be a blank line at the end
     Expression markers ("{", "}") and parentheses must be balanced
     All identifiers must be cnames (no spaces, quotes etc.)
    """

    class TransformTerminals(Transformer):
        # pylint: disable=invalid-name,no-self-use

        """Process terminal tokens"""
        def KEY(self, token):
            return token.update(value=token.value.rstrip(' ='))

        def NUMBER(self, token):
            return token.update(value=float(token.value))

        def INT(self, token):
            return token.update(value=int(token.value))

        def _extract_key(self, token):
            return token.update(value=token.value.split('=')[0].strip(' \t'))

        KVP_SCALAR_TAG = _extract_key
        KVP_BITS_TAG = _extract_key
        KVP_ARRAY_TAG = _extract_key
        KVP_STRING_TAG = _extract_key
        GAUGE_TAG = _extract_key

    def __init__(self):
        self._pre_processor = TsIniPreProcessor()
        self._ts_parser = Lark.open(_GRAMMAR,
                                    parser='lalr', debug=True,
                                    cache=str(_GRAMMAR_CACHE),
                                    transformer=TsIniParser.TransformTerminals())
        # Adapt the parser lexer to consume the preprocessor output (a Tree)
        self._ts_parser.parser.lexer = TreeLexerAdapter(self._ts_parser.parser.lexer)

    def define(self, symbol: str, value):
        """Define a preprocessor symbol to control preprocessing condtionals

        Equivalent of #set in the INI file. E.g.
          #set CAN_COMMANDS
        becomes
          define('CAN_COMMANDS', True)
        """

        self._pre_processor.define(symbol, value)

    def on_error(self, error_data):
        pass

    def parse(self, parse_source) -> Tree:
        preprocessed = self._pre_processor.pre_process(parse_source, on_error=self.on_error)
        return self._ts_parser.parse(preprocessed, on_error=self.on_error)
