from src.core.parser.Context import Context
# from src.core.Pipe import IllegalArgumentException
from src.core.Logger import Logger
from src.core.parser.InputStates_back import InputStates
from src.core.parser.Parser import ParserErrorException
InputStatesStatement = ""

class Splitter(Context):
    statements = set()

    def __init__(self, initial):
        if initial is None:
            # 我改变了这个地方，是一种取巧的方式
            raise ValueError("Illegal 'initial' argument in Splitter(State): " + str(initial))
        self.initial = initial
        self.state = None
        self.statements = set()
        self.stream = None

    def append(self, statement):
        # if statement is None:
        #     raise ValueError("Illegal 'statement' argument in Splitter.append(String): " + str(statement))
        self.statements.add(statement)

    def parse(self, stream):
        if stream is None:
            raise ValueError("Stream cannot be None")
        self.statements = set()
        self.stream = stream
        self.state = InputStates.INITIAL
        finished = False
        while not finished:
            finished = self.state.process(self)
        return self.statements

    def read(self):
        try:
            if self.stream is not None:
                char = self.stream.read(1)
                if char == '':
                    return -1
                return ord(char)
            return -1  # EOF

        except IOError:
            print("Cannot read from the input stream.")
            return -1
        except TypeError:
            print("Error processing the read character.")
        return -1

    # def read(self):
    #     if self.stream is None:
    #         raise ValueError("Stream is not set")
    #     try:
    #         char = self.stream.read(1)
    #         if char == '':
    #             return -1  # EOF
    #         return ord(char)
    #     except IOError:
    #         print("Cannot read from the input stream in Splitter.Read.")
    #     return -1

    def setState(self, next_state):
        global InputStatesStatement
        if next_state is None:
            raise ParserErrorException("Illegal 'next' argument in Splitter.setState(State): " + str(next_state))
        self.state = next_state

