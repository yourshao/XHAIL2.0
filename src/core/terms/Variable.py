from src.core.terms.Term import Term
from src.core.Buildable import Buildable

class Variable(Term):

    class Builder(Buildable):
        identifier = None
        type = None

        def __init__(self, identifier):
            identifier = identifier.strip()
            if identifier is None or identifier.strip() == "" or not ('A' <= identifier.strip()[0] <= 'Z'):
                raise ValueError(f"Illegal 'identifier' argument in Variable.Builder(identifier): {identifier}")
            self.identifier = identifier

        def build(self):
            return Variable(self)

        def set_content(self, identifier):
            identifier = identifier.strip()
            if identifier is None or identifier.strip() == "" or not ('A' <= identifier.strip()[0] <= 'Z'):
                raise ValueError(f"Illegal 'identifier' argument in Variable.Builder.set_content(identifier): {identifier}")
            self.identifier = identifier
            return self

        def set_type(self, types):
            if types is None:
                raise ValueError(f"Illegal 'type' argument in Variable.Builder.set_type(type): {types}")
            self.type = types
            return self

    identifier = None
    type = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Variable(builder): {builder}")
        self.identifier = builder.identifier
        self.type = builder.type

    def __eq__(self, other):
        if not isinstance(other, Variable):
            return NotImplemented
        if self.identifier != other.identifier:
            return False
        if self.type != other.type:
            return False
        return True

    def get_identifier(self):
        return self.identifier

    def get_type(self):
        return self.type

    def __hash__(self):
        prime = 31
        result = 1
        if self.identifier is None:
            result = prime * result
        else:
            result = prime * result + hash(self.identifier)
        if self.type is None:
            result = prime * result
        else:
            result = prime * result + hash(self.type)
        return result

    def __str__(self):
        return self.identifier

