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
        global InputStatesStatement
        if self == InputStates.INITIAL:
            InputStatesStatement = ""
            context.setState(InputStates.NORMAL)
            return False
        elif self == InputStates.NORMAL:
            ch = context.read()
            if ch == -1:
                context.append(InputStatesStatement)
                context.setState(InputStates.EOF)
            elif chr(ch) in ['\n', '\r', '\f']:
                pass
            elif chr(ch) in ['\t', ' ']:
                if InputStatesStatement and (InputStatesStatement.endswith("not") or
                                             InputStatesStatement.endswith("#compute") or
                                             InputStatesStatement.endswith("#const") or
                                             InputStatesStatement.endswith("#display") or
                                             InputStatesStatement.endswith("#domain") or
                                             InputStatesStatement.endswith("#example") or
                                             InputStatesStatement.endswith("#external") or
                                             InputStatesStatement.endswith("#hide") or
                                             InputStatesStatement.endswith("#modeb") or
                                             InputStatesStatement.endswith("#modeh") or
                                             InputStatesStatement.endswith("#show")):
                    InputStatesStatement += " "
            elif chr(ch) == '"':
                InputStatesStatement += chr(ch)
                context.setState(InputStates.STRING)
            elif chr(ch) == '.':
                InputStatesStatement += chr(ch)
                context.setState(InputStates.DOT)
            elif chr(ch) == '%':
                context.setState(InputStates.COMMENT)
            else:
                InputStatesStatement += chr(ch)
            return False
        elif self == InputStates.DOT:
            ch = context.read()
            if ch == -1:
                context.append(InputStatesStatement)
                context.setState(InputStates.EOF)
            elif chr(ch) in ['\n', '\r', '\f', '\t', ' ']:
                context.append(InputStatesStatement)
                InputStatesStatement = ""
                context.setState(InputStates.NORMAL)
            elif chr(ch) == '"':
                context.append(InputStatesStatement)
                InputStatesStatement = chr(ch)
                context.setState(InputStates.STRING)
            elif chr(ch) == '.':
                InputStatesStatement += chr(ch)
                context.setState(InputStates.NORMAL)
            elif chr(ch) == '%':
                context.append(InputStatesStatement)
                InputStatesStatement = ""
                context.setState(InputStates.COMMENT)
            else:
                context.append(InputStatesStatement)
                InputStatesStatement = chr(ch)
                context.setState(InputStates.NORMAL)
            return False
        elif self == InputStates.STRING:
            ch = context.read()
            if ch == -1:
                context.append(InputStatesStatement)
                context.setState(InputStates.EOF)
            elif chr(ch) == '\\':
                InputStatesStatement += chr(ch)
                context.setState(InputStates.ESCAPE)
            elif chr(ch) == '"':
                InputStatesStatement += chr(ch)
                context.setState(InputStates.NORMAL)
            else:
                InputStatesStatement += chr(ch)
            return False
        elif self == InputStates.ESCAPE:
            ch = context.read()
            if ch == -1:
                context.append(InputStatesStatement)
                context.setState(InputStates.EOF)
            else:
                InputStatesStatement += chr(ch)
                context.setState(InputStates.STRING)
            return False
        elif self == InputStates.COMMENT:
            ch = context.read()
            if ch == -1:
                context.append(InputStatesStatement)
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
                context.append(InputStatesStatement)
                context.setState(InputStates.EOF)
            elif chr(ch) == '\n':
                context.setState(InputStates.NORMAL)
            return False
        elif self == InputStates.COMMENT_MULTI:
            ch = context.read()
            if ch == -1:
                context.append(InputStatesStatement)
                context.setState(InputStates.EOF)
            elif chr(ch) == '*':
                context.setState(InputStates.COMMENT_OVER)
            return False
        elif self == InputStates.COMMENT_OVER:
            ch = context.read()
            if ch == -1:
                context.append(InputStatesStatement)
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
