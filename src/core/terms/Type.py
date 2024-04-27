import enum
# from

class Type(enum.Enum):

    CONSTANT = ("$", "CONSTANT_STRING")
    INPUT = ("+", "INPUT_STRING")
    OUTPUT = ("-", "OUTPUT_STRING")

    def __init__(self, symbol, internal):
        self.symbol = symbol
        self.internal = internal

    def get_internal(self):
        return self.internal

    def __str__(self):
        return self.symbol
