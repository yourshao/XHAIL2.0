
import enum

from src.core.Logger_copy import Logger

TokeniserStateToken: str = ''


class TokeniserState(enum.Enum):
    EOF = enum.auto()
    ESCAPE = enum.auto()
    NORMAL = enum.auto()
    SKIP = enum.auto()
    STRING = enum.auto()

    def process(self, tokeniser):
        global TokeniserStateToken
        if self == TokeniserState.EOF:
            tokeniser.set_token(None)
            tokeniser.set_state(TokeniserState.EOF)
            return True
        elif self == TokeniserState.ESCAPE:
            ch = tokeniser.read()
            if ch == -1:
                tokeniser.set_token(TokeniserStateToken)
                tokeniser.set_state(TokeniserState.EOF)
                return False
            else:
                TokeniserStateToken += chr(ch)
                tokeniser.set_state(TokeniserState.STRING)
                return False
        elif self == TokeniserState.NORMAL:
            ch = tokeniser.read()
            if ch == -1:
                tokeniser.set_token(TokeniserStateToken)
                tokeniser.set_state(TokeniserState.EOF)
                return False
            elif ch == ord('"'):
                TokeniserStateToken += chr(ch)
                tokeniser.set_state(TokeniserState.STRING)
                return False
            # elif ch in (ord('\r'), ord('\n'), ord(' ')):
            elif ch in (10, 13, 32):
                tokeniser.set_token(TokeniserStateToken)
                tokeniser.set_state(TokeniserState.SKIP)
                TokeniserStateToken = ""
                return True
            else:
                TokeniserStateToken += chr(ch)
                return False
        elif self == TokeniserState.SKIP:
            ch = tokeniser.read()
            if -1 == ch:
                tokeniser.set_token(TokeniserStateToken)
                tokeniser.set_state(TokeniserState.EOF)
                return False
            elif ch in (ord('\r'), ord('\n'), ord(' ')):
                return False
            else:
                TokeniserStateToken += chr(ch)
                tokeniser.set_state(TokeniserState.NORMAL)
                return False
        elif self == TokeniserState.STRING:
            ch = tokeniser.read()
            if ch == -1:
                tokeniser.set_token(TokeniserStateToken)
                tokeniser.set_state(TokeniserState.EOF)
                return False
            elif ch == ord('\\'):
                TokeniserStateToken += chr(ch)
                tokeniser.set_state(TokeniserState.ESCAPE)
                return False
            elif ch == ord('"'):
                TokeniserStateToken += chr(ch)
                tokeniser.set_state(TokeniserState.NORMAL)
                return False
            else:
                if tokeniser.token is None:
                    TokeniserStateToken = ""
                TokeniserStateToken += chr(ch)
                return False






class Tokeniser:
    state = None
    token = None
    @staticmethod
    def from_stream(stream):
        if stream is None:
            raise ValueError("Illegal 'stream' argument in Tokeniser.from_stream(InputStream): " + str(stream))
        return Tokeniser(stream)

    def __init__(self, stream):
        if stream is None:
            raise ValueError("Illegal 'stream' argument in Tokeniser.__init__(InputStream): " + str(stream))
        self.stream = stream
        self.set_state(TokeniserState.SKIP)

    def next(self):
        finished = False
        while not finished:
            finished = self.state.process(self)
        return self.token

    def read(self):
        try:
            char = self.stream.read(1)
            if char == '':
                return -1  # EOF
            return ord(char)
        except IOError:
            print("Cannot read from the input stream.")
            return -1
        except TypeError:
            print("Error processing the read character.")
        return -1

    def set_state(self, next_state):
        if next_state is None:
            raise ValueError("Illegal 'next' argument in Tokeniser.set_state(State): " + str(next_state))
        self.state = next_state

    def set_token(self, token):
        self.token = token


#
#
# class TokeniserState(enum.Enum):
#     EOF = enum.auto()
#     ESCAPE = enum.auto()
#     NORMAL = enum.auto()
#     SKIP = enum.auto()
#     STRING = enum.auto()
#
#     def process(self, tokeniser):
#         if self == TokeniserState.EOF:
#             tokeniser.set_token(None)
#             tokeniser.set_state(TokeniserState.EOF)
#             return True
#         elif self == TokeniserState.ESCAPE:
#             ch = tokeniser.read()
#             if ch == -1:
#                 tokeniser.set_token(tokeniser.token)
#                 tokeniser.set_state(TokeniserState.EOF)
#                 return False
#             else:
#                 if tokeniser.token is None:
#                     tokeniser.token = ""
#                 tokeniser.token += chr(ch)
#                 tokeniser.set_state(TokeniserState.STRING)
#                 return False
#         elif self == TokeniserState.NORMAL:
#             ch = tokeniser.read()
#             if ch == -1:
#                 tokeniser.set_token(tokeniser.token)
#                 tokeniser.set_state(TokeniserState.EOF)
#                 return False
#             elif ch == ord('"'):
#                 if tokeniser.token is None:
#                     tokeniser.token = ""
#                 tokeniser.token += chr(ch)
#                 tokeniser.set_state(TokeniserState.STRING)
#                 return False
#             elif ch in (ord('\r'), ord('\n'), ord(' ')):
#                 tokeniser.set_token(tokeniser.token)
#                 tokeniser.set_state(TokeniserState.SKIP)
#                 tokeniser.token = ""
#                 return True
#             else:
#                 if tokeniser.token is None:
#                     tokeniser.token = ""
#                 tokeniser.token += chr(ch)
#                 return False
#         elif self == TokeniserState.SKIP:
#             ch = tokeniser.read()
#             if -1 == ch:
#                 tokeniser.set_token(tokeniser.token)
#                 tokeniser.set_state(TokeniserState.EOF)
#                 return False
#             elif ch in (ord('\r'), ord('\n'), ord(' ')):
#                 return False
#             else:
#                 if tokeniser.token is None:
#                     tokeniser.token = ""
#                 tokeniser.token += chr(ch)
#                 tokeniser.set_state(TokeniserState.NORMAL)
#                 return False
#         elif self == TokeniserState.STRING:
#             ch = tokeniser.read()
#             if ch == -1:
#                 tokeniser.set_token(tokeniser.token)
#                 tokeniser.set_state(TokeniserState.EOF)
#                 return False
#             elif ch == ord('\\'):
#                 if tokeniser.token is None:
#                     tokeniser.token = ""
#                 tokeniser.token += chr(ch)
#                 tokeniser.set_state(TokeniserState.ESCAPE)
#                 return False
#             elif ch == ord('"'):
#                 if tokeniser.token is None:
#                     tokeniser.token = ""
#                 tokeniser.token += chr(ch)
#                 tokeniser.set_state(TokeniserState.NORMAL)
#                 return False
#             else:
#                 if tokeniser.token is None:
#                     tokeniser.token = ""
#                 tokeniser.token += chr(ch)
#                 return False
