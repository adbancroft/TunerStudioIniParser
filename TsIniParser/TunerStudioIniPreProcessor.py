from lark import Lark, Transformer, Tree
from more_itertools import first_true
from pathlib import Path

_GRAMMAR = Path(__file__).parent / 'pre_processor.lark'
_GRAMMAR_CACHE = _GRAMMAR.with_suffix('.lark.cache')

class TsIniPreProcessor:
    """TunserStudio INI file pre-processpr

    The TS INI file uses pre-processing directives to include or exclude lines
        E.g. #if CAN_COMMANDS
    This class will process a TS INI file and apply the conditional pre-processing
    directives.
    """

    class pp_transformer(Transformer):
        """Transformer for the preprocessor grammar.
        
        Will apply #if directives to include/exclude lines from the source file.
        """

        def __init__(self, symbol_table):
            self._symbol_table = symbol_table

        def pp_conditional(self, children):
            """Process pp_conditional tree object"""

            # The other rule processors will have applied the conditional tests
            # and generated either ppif_body or empty trees. An If/ElseIf combo
            # may generate more than one ppif_body, so pick the first one - this will
            # be the first that evaluated to True which is the same logic the
            # C preprocessor uses. 
            return first_true(children, pred=lambda c: c)

        def if_part(self, children):
            """Process if_part tree object"""

            # Various sub rules will have set the first child to either true or false.
            # i.e. the if condition is already evaluated.
            if children[0]:
                return children[1]
            return
        
        def _ifndef_line(self, children):
            """#ifndef directive"""
            return [not children[0]]
      
        def elif_part(self, children):
            """Process elif_part tree object"""
            if children[0]:
                return children[1]
            return

        def set(self, children):
            """Process #set directive"""
            self._symbol_table[children[0].value] = True
            return

        def unset(self, children):
            """Process #unset directive"""
            identifier = children[0].value
            if  identifier in self._symbol_table.keys():
                del self._symbol_table[identifier]
            return

        def symbol(self, children):
            """ Process a symbol test"""
            return children[0].value in self._symbol_table.keys()

        def expression(self, children):
            """Process an expression
            
            Currently we only support (symbol | !symbol)
            """
            if len(children)>1: # Negated 
                return not (children[1].value in self._symbol_table.keys())
            return children[0].value in self._symbol_table.keys()

    def __init__(self):
        self._symbol_table = {}
        self.processor = Lark.open(_GRAMMAR, parser='lalr', debug = True, transformer = TsIniPreProcessor.pp_transformer(self._symbol_table), cache = str(_GRAMMAR_CACHE))

    def define(self, symbol:str, value):
        """Define a preprocessor symbol to control preprocessing condtionals

        Equivalent of #set in the INI file. E.g.
          #set CAN_COMMANDS
        becomes
          define('CAN_COMMANDS', True)
        """
        
        self._symbol_table[symbol] = value

    def pre_process(self, input, on_error=None) -> Tree:
        return self.processor.parse(input, on_error = on_error)