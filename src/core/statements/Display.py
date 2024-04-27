from src.core.Buildable import Buildable


class Display:

    class Builder(Buildable):


        identifier = None

        def __init__(self, identifier):
            self.arity = 1
            identifier = identifier.strip()
            if identifier is None or identifier == "" or not ('a' <= identifier[0] <= 'z'):
                raise ValueError(f"Illegal 'identifier' argument in Display.Builder(identifier): {identifier}")
            self.identifier = identifier

        def build(self):
            return Display(self)

        def set_arity(self, arity):
            if arity < 0:
                raise ValueError(f"Illegal 'builder' argument in Display.Builder.set_arity(): {self.arity}")
            self.arity = arity
            return self

        def set_identifier(self, identifier):
            identifier = identifier.strip()
            if identifier is None or identifier == "" or not ('a' <= identifier[0] <= 'z'):
                raise ValueError(f"Illegal 'identifier' argument in Display.Builder.set_identifier(): {identifier}")
            self.identifier = identifier


    KEYWORD = "#display"
    arity = None
    identifier = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Display(builder): {builder}")
        self.identifier = builder.identifier
        self.arity = builder.arity

    def as_clauses(self):
        result = ""
        for i in range(1, self.arity + 1):
            if i > 1:
                result += ","
            result += f"V{i}"
        if result:
            result = f"({result})"
        result = self.identifier + result
        return f"display_fact({result}):-{result}."

    def compare_to(self, other):
        result = self.identifier.compare_to(other.identifier)
        if result == 0:
            result = other.arity - self.arity
        return result

    def __eq__(self, other):
        if not isinstance(other, Display):
            return False
        if self.arity != other.arity:
            return False
        if self.identifier != other.identifier:
            return False
        return True

    def get_arity(self):
        return self.arity

    def get_identifier(self):
        return self.identifier

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + self.arity
        result = prime * result + 0 if self.identifier is None else hash(self.identifier)
        return result

    def __str__(self):
        return f"{self.KEYWORD} {self.identifier}/{self.arity}."





