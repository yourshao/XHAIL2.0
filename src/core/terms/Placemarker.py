from enum import Enum
from src.core.Buildable import Buildable
from src.core.terms.Type import Type
from src.core.terms.Scheme import Scheme
from src.core.terms.Variable import Variable
from src.core.terms.SchemeTerm import SchemeTerm


class Placemarker(SchemeTerm):

    class Builder(Buildable):

        def __init__(self, identifier):
            self.type = Type.CONSTANT
            identifier = identifier.strip()
            if identifier is None or identifier == "" or not ('a' <= identifier.strip()[0] <= 'z'):
                raise ValueError("Identifier cannot be None or empty")
            else:
                self.identifier = identifier

        def build(self):
            return Placemarker(self)

        def set_identifier(self, identifier):
            identifier = identifier.strip()
            if identifier is None or identifier == "" or not ('A' <= identifier.strip()[0] <= 'Z'):
                raise ValueError("Identifier cannot be None or empty")
            self.identifier = identifier
            return self

        def set_type(self, types):
            if types is None:
                raise ValueError("Type cannot be None")
            else:
                self.type = types
                return self

    CONSTANT_STRING = "internal_const_par"
    INPUT_STRING = "internal_input_par"
    OUTPUT_STRING = "internal_output_par"

    identifier = None
    type = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError("Builder cannot be None")
        self.identifier = builder.identifier
        self.type = builder.type

    def decode(self):
        term = Scheme.Builder(self.identifier).build()
        return Scheme.Builder(self.type.get_internal()).add_term(term).build()

    def __eq__(self, other):
        if not isinstance(other, Placemarker):
            return NotImplemented
        if self.identifier != other.identifier:
            return False
        if self.type != other.type:
            return False
        return True

    def generalises(self, *args):
        if len(args) == 1:
            set = args[0]
            if set is None:
                raise f"Illegal 'set' argument in Placemarker.generalises(Set<Variable>): {set}"
            set_size = len(set)
            var = Variable.Builder("V" + str(1 + set_size)).set_type(self).build()
            set.add(var)
            return var
        elif len(args) == 2:
            term = args[0]
            map = args[1]
            if term is None:
                raise f"Illegal 'term' argument in Placemarker.generalises(Term, Map<Variable, Variable>): {term}"
            if map is None:
                raise f"Illegal 'map' argument in Placemarker.generalises(Term, Map<Variable, Variable>): {map}"

            if Type == self.type or Type.OUTPUT == self.type:
                var = map.get(term)
                if var is None:
                    identifier = "V" + str(1 + len(map))
                    var = Variable.Builder(identifier).set_type(self).build()
                    map[term] = var
                return var
            else:
                return term

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
        return f"{self.type}{self.identifier}"

    def is_placemarker(self):
        return True













