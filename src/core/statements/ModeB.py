from src.core.Buildable import Buildable

class ModeB():

    class Builder(Buildable):

        negated = False
        priority = 1
        scheme = None
        upper = float('inf')
        weight = 1

        def __init__(self, scheme):
            if scheme is None:
                raise ValueError(f"Illegal 'scheme' argument in ModeB.Builder(scheme): {scheme}")
            self.scheme = scheme

        def __build__(self):
            return ModeB(self)

        def set_negated(self, negated):
            self.negated = negated
            return self

        def set_priority(self, priority):
            self.priority = priority
            return self

        def set_scheme(self, scheme):
            if scheme is None:
                raise ValueError(f"Illegal 'scheme' argument in ModeB.Builder.set_scheme(scheme): {scheme}")
            self.scheme = scheme
            return self

        def set_upper(self, upper):
            self.upper = upper
            return self

        def set_weight(self, weight):
            self.weight = 1 if weight is None else weight
            return self

        def build(self):
            return ModeB(self)

    CONSTRAINT_OP = ":"
    KEYWORD = "#modeb"
    PRIORITY_OP = "@"
    SEPARATOR_OP = "-"
    WEIGHT_OP = "="

    negated = False
    priority = None
    scheme = None
    upper = None
    weight = None

    def __init__(self, builder):
        self.negated = builder.negated
        self.priority = builder.priority
        self.scheme = builder.scheme
        self.upper = builder.upper
        self.weight = builder.weight

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, ModeB):
            return False
        return (self.negated == other.negated and
                self.priority == other.priority and
                self.scheme == other.scheme and
                self.upper == other.upper and
                self.weight == other.weight)

    def get_priority(self):
        return self.priority

    def get_scheme(self):
        return self.scheme

    def get_weight(self):
        return self.weight

    def get_upper(self):
        return self.upper

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (1231 if self.negated else 1237)
        result = prime * result + self.priority
        result = prime * result + (0 if self.scheme is None else hash(self.scheme))
        # result = prime * result + self.upper
        result = prime * result + self.weight
        return result

    def is_negated(self):
        return self.negated

    def __str__(self):
        result = self.KEYWORD  # 假设有一个适当的关键词，如 "modeb"
        if self.negated:
            result += " not"
        result += " " + str(self.scheme)
        if self.upper != float('inf'):
            result += " :{}".format(self.upper)
        if self.weight != 1:
            result += " ={0}".format(self.weight)
        if self.priority != 1:
            result += " @{0}".format(self.priority)
        result += "."
        return result

    


















