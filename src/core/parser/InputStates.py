from enum import Enum


class InputStates(Enum):
    INITIAL = 1
    NORMAL = 2
    DOT = 3
    STRING = 4
    ESCAPE = 5
    COMMENT = 6
    COMMENT_SINGLE = 7
    COMMENT_MULTI = 8
    COMMENT_OVER = 9
    EOF = 10

    def process(self, context):
        if self == InputStates.INITIAL:
            InputStates.statement = ""
            context.setState(InputStates.NORMAL)
            return False
        elif self == InputStates.NORMAL:
            ch = context.read()
            if ch == -1:
                context.append(self.statement)
                context.setState(InputStates.EOF)
            elif chr(ch) in ['\n', '\r', '\f']:
                pass
            elif chr(ch) in ['\t', ' ']:
                if self.statement and (self.statement.endswith("not") or
                                       self.statement.endswith("#compute") or
                                       self.statement.endswith("#const") or
                                       self.statement.endswith("#display") or
                                       self.statement.endswith("#domain") or
                                       self.statement.endswith("#example") or
                                       self.statement.endswith("#external") or
                                       self.statement.endswith("#hide") or
                                       self.statement.endswith("#modeb") or
                                       self.statement.endswith("#modeh") or
                                       self.statement.endswith("#show")):
                    self.statement += " "
            elif chr(ch) == '"':
                self.statement += chr(ch)
                context.setState(InputStates.STRING)
            elif chr(ch) == '.':
                self.statement += chr(ch)
                context.setState(InputStates.DOT)
            elif chr(ch) == '%':
                context.setState(InputStates.COMMENT)
            else:
                self.statement += chr(ch)
            return False
        elif self == InputStates.DOT:
            ch = context.read()
            if ch == -1:
                context.append(self.statement)
                context.setState(InputStates.EOF)
            elif chr(ch) in ['\n', '\r', '\f', '\t', ' ']:
                context.append(self.statement)
                self.statement = ""
                context.setState(InputStates.NORMAL)
            elif chr(ch) == '"':
                context.append(self.statement)
                self.statement = chr(ch)
                context.setState(InputStates.STRING)
            elif chr(ch) == '.':
                self.statement += chr(ch)
                context.setState(InputStates.NORMAL)
            elif chr(ch) == '%':
                context.append(self.statement)
                self.statement = ""
                context.setState(InputStates.COMMENT)
            else:
                context.append(self.statement)
                self.statement = chr(ch)
                context.setState(InputStates.NORMAL)
            return False
        elif self == InputStates.STRING:
            ch = context.read()
            if ch == -1:
                context.append(self.statement)
                context.setState(InputStates.EOF)
            elif chr(ch) == '\\':
                self.statement += chr(ch)
                context.setState(InputStates.ESCAPE)
            elif chr(ch) == '"':
                self.statement += chr(ch)
                context.setState(InputStates.NORMAL)
            else:
                self.statement += chr(ch)
            return False
        elif self == InputStates.ESCAPE:
            ch = context.read()
            if chr(ch) == -1:
                context.append(self.statement)
                context.setState(InputStates.EOF)
            else:
                self.statement += chr(ch)
                context.setState(InputStates.STRING)
            return False
        elif self == InputStates.COMMENT:
            ch = context.read()
            if ch == -1:
                context.append(self.statement)
                context.setState(InputStates.EOF)
            elif chr(ch) == '\n':
                context.setState(InputStates.NORMAL)
            elif chr(ch) == '*':
                context.setState(InputStates.COMMENT_MULTI)
            else:
                context.setState(InputStates.COMMENT_SINGLE)
            return False
        elif self == InputStates.COMMENT_SINGLE:
            ch = context.read()
            if ch == -1:
                context.append(self.statement)
                context.setState(InputStates.EOF)
            elif chr(ch) == '\n':
                context.setState(InputStates.NORMAL)
            return False
        elif self == InputStates.COMMENT_MULTI:
            ch = context.read()
            if ch == -1:
                context.append(self.statement)
                context.setState(InputStates.EOF)
            elif chr(ch) == '*':
                context.setState(InputStates.COMMENT_OVER)
            return False
        elif self == InputStates.COMMENT_OVER:
            ch = context.read()
            if ch == -1:
                context.append(self.statement)
                context.setState(InputStates.EOF)
            elif chr(ch) == '%':
                context.setState(InputStates.NORMAL)
            elif chr(ch) == '*':
                pass
            else:
                context.setState(InputStates.COMMENT_MULTI)
            return False
        elif self == InputStates.EOF:
            context.setState(InputStates.EOF)
            return True
        else:
            print("Hello world!")
            return True
