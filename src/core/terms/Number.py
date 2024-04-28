from src.core.Buildable import Buildable
from src.core.terms.Term import Term



class Number(Term):

    class Builder(Buildable):
        value = None

        def __init__(self, value):
            self.value = value

        def build(self):
            return Number(self)

        def set_value(self, value):
            self.value = value
            return self

    value = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Number(builder): {builder}")
        self.value = builder.value

    def __eq__(self, other):
        if not isinstance(other, Number):
            return False
        if other is None:
            return False
        if self is other:
            return True
        return self.value == other.value

    def generalises(self, *args):
        if len(args) == 1:
            sets = args[0]
            if sets is None:
                raise ValueError(f"Illegal 'set' argument in Number.generalises(set): {sets}")

        elif len(args) == 2:
            term = args[0]
            maps = args[1]
            if term is None:
                raise ValueError(f"Illegal 'term' argument in Number.generalises(term, map): {term}")
            if maps is None:
                raise ValueError(f"Illegal 'map' argument in Number.generalises(term, map): {maps}")
            if isinstance(term, Number):
                if self.value == term.get_value():
                    return self
                else:
                    return None
            else:
                return None

    def get_value(self):
        return self.value

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + self.value
        return result

    def __str__(self):
        return f"{self.value}"

    def compare_to(self, other):
        if other is None:
            return 1
        return self.value - other.value


