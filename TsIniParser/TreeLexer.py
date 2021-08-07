from lark.lexer import Lexer, Token, LineCounter
from contextlib import suppress

class TokenLexerAdapter(Lexer):
    __future_interface__ = True

    def __init__(self, inner_lexer):
        self._inner_lexer = inner_lexer
        self._input_tokens = None
        self._cur_input_token = None

    def lex(self, lexer_state, parser_state):
        while self._feed_next_input_token(lexer_state):
            with suppress(StopIteration):
                inner_tokenizer = self._inner_lexer.lex(lexer_state, parser_state)
                while True:
                    yield self._adjust_token_pos(next(inner_tokenizer))

    def make_lexer_state(self, tokens):
        self._input_tokens = tokens
        return self._inner_lexer.make_lexer_state("")

    def _feed_next_input_token(self, lexer_state):
        try:
            self._cur_input_token = next(self._input_tokens)
            lexer_state.text = self._cur_input_token.value
            lexer_state.line_ctr = LineCounter('\n')
            lexer_state.line_ctr.line = self._cur_input_token.line
            return True
        except StopIteration:
            return False

    def _adjust_token_pos(self, token):
        token.pos_in_stream = token.pos_in_stream + self._cur_input_token.pos_in_stream
        token.end_pos = token.end_pos + self._cur_input_token.pos_in_stream
        token.column = token.column + self._cur_input_token.column - 1
        token.end_column = token.end_column + self._cur_input_token.column - 1
        return token                

class TreeLexerAdapter(TokenLexerAdapter):
    __future_interface__ = True

    def __init__(self, inner_lexer):
        super().__init__(inner_lexer)

    def lex(self, lexer_state, parser_state):
        return super().lex(lexer_state, parser_state)

    def make_lexer_state(self, tree):
        return super().make_lexer_state(tree.scan_values(lambda v: isinstance(v, Token)))