from contextlib import suppress
from io import TextIOBase
from lark.lexer import Lexer


class TextIoLexer(Lexer):

    __future_interface__ = True

    def __init__(self, inner_lexer: Lexer):
        self._inner_lexer = inner_lexer
        self._input = None
        self._char_offset = 0

    def lex(self, lexer_state, parser_state):
        # pylint: disable=stop-iteration-return
        while self._feed_next_line(lexer_state):
            with suppress(StopIteration):
                inner_tokenizer = self._inner_lexer.lex(lexer_state,
                                                        parser_state)
                while True:
                    yield self._adjust_token_pos(next(inner_tokenizer))

    def _feed_next_line(self, lexer_state):
        self._char_offset += lexer_state.line_ctr.char_pos
        lexer_state.text = self._input.readline()
        lexer_state.line_ctr.char_pos = 0
        lexer_state.line_ctr.column = 1
        lexer_state.line_ctr.line_start_pos = 0
        return lexer_state.text != ''

    def _adjust_token_pos(self, token):
        token.start_pos = token.start_pos + self._char_offset
        token.end_pos = token.end_pos + self._char_offset
        return token

    def make_lexer_state(self, text: TextIOBase):
        self._input = text
        state = self._inner_lexer.make_lexer_state('')
        self._char_offset = state.line_ctr.char_pos
        return state
