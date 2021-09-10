from pathlib import Path
from lark import Lark, Transformer, Tree, Token
from .text_io_lexer import TextIoLexer

_GRAMMAR = Path(__file__).parent / 'grammars' / 'pre_processor.lark'
_GRAMMAR_CACHE = _GRAMMAR.with_suffix('.lark.cache')


class TsIniPreProcessor:
    """TunserStudio INI file pre-processpr

    The TS INI file uses pre-processing directives to include or exclude lines
        E.g. #if CAN_COMMANDS
    This class will process a TS INI file and apply the conditional
    pre-processing directives.
    """

    class PreProcessorTransformer(Transformer):
        # pylint: disable=no-self-use
        """Transformer for the preprocessor grammar.

        Will apply #if directives to include/exclude lines from the
        source file.
        """

        def __init__(self, symbol_table, ignore_hash_error: bool):
            super().__init__()
            self._symbol_table = symbol_table
            self._ignore_hash_error = ignore_hash_error
            self._parse_source = None

        def pp_conditional(self, children):

            """Process pp_conditional tree object"""

            def is_token(item, token_type_name: str) -> bool:
                return isinstance(item, Token) and item.type == token_type_name

            # The other rule processors will have applied the conditional
            # tests and generated either ppif_body or empty trees.
            # An If/ElseIf combo may generate more than one ppif_body, so
            # pick the first one - this will be the first that evaluated to
            # True which is the same logic the C preprocessor uses.
            selected_body = [child for child in children if child]
            selected_body = selected_body[0] if selected_body else None

            # Check for any error directives from the INI file
            # We only expect these inside a pre-processor conditional
            if selected_body:
                errors = list(selected_body.scan_values(lambda v: is_token(v, 'ERROR_MSG')))
                if errors:
                    raise SyntaxError('#error directive triggered',
                                      (self._parse_source,
                                       errors[0].line,
                                       errors[0].column,
                                       errors[0].value))
                exit_directives = list(selected_body.scan_values(lambda v: is_token(v, 'EXIT_TAG')))
                if exit_directives:
                    raise SyntaxError('#exit directive triggered',
                                      (self._parse_source,
                                       exit_directives[0].line,
                                       exit_directives[0].column,
                                       exit_directives[0].value))

            return selected_body

        def if_part(self, children):
            """Process if_part tree object"""

            # Various sub rules will have set the first child to either
            # true or false.
            # i.e. the if condition is already evaluated.
            if children[0]:
                return children[1]
            return None

        def elif_part(self, children):
            """Process elif_part tree object"""
            if children[0]:
                return children[1]
            return None

        def set(self, children):
            """Process #set directive"""
            self._symbol_table[children[0].value] = True

        def unset(self, children):
            """Process #unset directive"""
            identifier = children[0].value
            if identifier in self._symbol_table.keys():
                del self._symbol_table[identifier]

        def symbol(self, children):
            """ Process a symbol test"""
            return children[0].value in self._symbol_table.keys()

        def expression(self, children):
            """Process an expression

            Currently we only support (symbol | !symbol)
            """
            if len(children) > 1:  # Negated
                return not children[1].value in self._symbol_table.keys()
            return children[0].value in self._symbol_table.keys()

        def include(self, children):
            # pylint: disable=unused-argument
            # Just skip includes for now
            return None

        def error(self, children):
            if self._ignore_hash_error:
                return None
            return Tree('error', children)

        def exit(self, children):
            if self._ignore_hash_error:
                return None
            return Tree('exit', children)

        def set_parse_source(self, parse_source):
            self._parse_source = parse_source

    def __init__(self, ignore_hash_error: bool):
        self._symbol_table = {}
        self._pp_transformer = TsIniPreProcessor.PreProcessorTransformer(self._symbol_table, ignore_hash_error)
        self._processor = Lark.open(_GRAMMAR, parser='lalr',
                                    transformer=self._pp_transformer,
                                    cache=str(_GRAMMAR_CACHE))
        self._processor.parser.lexer = TextIoLexer(self._processor.parser.lexer)

    def define(self, symbol: str, value):
        """Define a preprocessor symbol to control preprocessing condtionals

        Equivalent of #set in the INI file. E.g.
          #set CAN_COMMANDS
        becomes
          define('CAN_COMMANDS', True)
        """

        self._symbol_table[symbol] = value

    def pre_process(self, parse_source, on_error=None) -> Tree:
        self._pp_transformer.set_parse_source(parse_source)
        return self._processor.parse(parse_source, on_error=on_error)
