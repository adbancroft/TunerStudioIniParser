from lark.lexer import Lexer
from io import TextIOBase
from contextlib import suppress

class TextIoLexer(Lexer):
    __future_interface__ = True

    def __init__(self, inner_lexer):
        self._inner_lexer = inner_lexer
        self._input = None

    def lex(self, lexer_state, parser_state):
        while self._feed_next_line(lexer_state):
            with suppress(StopIteration):
                inner_tokenizer = self._inner_lexer.lex(lexer_state, parser_state)
                while True:
                    yield self._adjust_token_pos(next(inner_tokenizer))        

    def _feed_next_line(self, lexer_state):
        self._char_offset += lexer_state.line_ctr.char_pos
        lexer_state.text = self._input.readline()
        lexer_state.line_ctr.char_pos = 0
        lexer_state.line_ctr.column = 1
        lexer_state.line_ctr.line_start_pos = 0
        return lexer_state.text!=''

    def _adjust_token_pos(self, token):
        token.pos_in_stream = token.pos_in_stream + self._char_offset
        token.end_pos = token.end_pos + self._char_offset
        return token          

    def make_lexer_state(self, io : TextIOBase):
        self._input = io
        state = self._inner_lexer.make_lexer_state('')
        self._char_offset = state.line_ctr.char_pos
        return state