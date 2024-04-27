from src.core.Buildable import Buildable
from src.core.LinkedHashSet import LinkedHashSet
from src.core.terms.Atom import Atom
# from src.core.terms.Placemarker import Placemarker
# from src.core.terms.Quotation import Quotation
from src.core.terms.Number import Number

CONSTANT_STRING = "internal_const_par"
INPUT_STRING = "internal_input_par"
OUTPUT_STRING = "internal_output_par"


class Scheme:

    class Builder(Buildable):
        identifier = None
        negated = False
        terms = []

        def __init__(self, identifier):
            identifier = identifier.strip()
            if identifier is None or identifier.strip() == "" or not ('a' <= identifier.strip()[0] <= 'z'):
                raise ValueError(f"Illegal 'identifier' argument in Scheme.Builder(identifier): {identifier}")
            self.identifier = identifier
            self.terms = []

        def add_term(self, term):
            if term is None:
                raise ValueError(f"Illegal 'term' argument in Scheme.Builder.add_term(term): {term}")
            else:
                self.terms.append(term)
                return self

        def add_terms(self, terms):
            if terms is None:
                raise ValueError(f"Illegal 'terms' argument in Scheme.Builder.add_terms(terms): {terms}")
            for term in terms:
                self.terms.extend(term)
            return self

        def build(self):
            return Scheme(self)

        def clear_terms(self):
            self.terms.clear()
            return self

        def remove_term(self, term):
            if term is None:
                raise ValueError(f"Illegal 'term' argument in Scheme.Builder.remove_term(term): {term}")
            self.terms.remove(term)
            return self

        def set_identifier(self, identifier):
            if identifier is None or identifier.strip() == "" or not ('a' <= identifier.strip()[0] <= 'z'):
                raise ValueError(f"Illegal 'identifier' argument in Scheme.Builder.set_identifier(identifier): {identifier}")
            self.identifier = identifier
            return self

        def set_negated(self, negated):
            self.negated = negated
            return self

    identifier = None
    negated = None
    terms = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Scheme(builder): {builder}")
        self.identifier = builder.identifier
        self.negated = builder.negated
        self.terms = builder.terms

    def __eq__(self, other):
        if self is other:
            return True
        if other is None or not isinstance(other, Scheme):
            return False
        if self.identifier != other.identifier:
            return False
        if self.negated != other.negated:
            return False
        if len(self.terms) != len(other.terms):
            return False
        for i in range(len(self.terms)):
            if self.terms[i] != other.terms[i]:
                return False
        return True

    def generalises(self, *args):
        if len(args) == 0 or len(args) > 2:
            return False
        elif len(args) == 1:
            sets = args[0]
            if sets is None:
                raise ValueError(f"Illegal 'sets' argument in Scheme.generalises(sets): {sets}")
            else:
                builder = Atom.Builder(self.identifier).set_scheme(self)
                for i in range(len(self.terms)):
                    nested = self.terms[i].generalises(sets)
                    if nested is None:
                        return None
                    builder.add_term(nested)
                return builder.build()
        elif len(args) == 2:
            term = args[0]
            maps = args[1]
            if term is None:
                raise ValueError(f"Illegal 'term' argument in Scheme.generalises(term, maps): {term}")
            if maps is None:
                raise ValueError(f"Illegal 'maps' argument in Scheme.generalises(term, maps): {maps}")
            if isinstance(term, Atom):
                if term.get_identifier() == self.identifier and term.get_arity() == len(self.terms):
                    builder = Atom.Builder(term).clear_terms()
                    for i in range(len(self.terms)):
                        nested = self.terms[i].generalises(term.get_term(i), maps)
                        if nested is None:
                            return None
                        builder.add_term(nested)
                    return builder.build()
                else:
                    return None
            else:
                return None

    def get_arity(self):
        return len(self.terms)

    def get_identifier(self):
        return self.identifier

    def get_term(self, index):
        if index < 0 or index >= len(self.terms):
            raise ValueError(f"Illegal 'index' argument in Scheme.get_term(index): {index}")
        return self.terms[index]

    def get_terms(self):
        return self.terms

    def __hash__(self):
        prime = 31
        result = 1
        if self.identifier is not None:
            result = prime * result + hash(self.identifier)
        else:
            result = prime * result
        if self.negated is False:
            result = prime * result + 1237
        else:
            result = prime * result + 1231
        result = prime * result + hash(tuple(self.terms))
        return result

    def is_negated(self):
        return self.negated

    def is_placemarker(self):
        first = CONSTANT_STRING == self.identifier or INPUT_STRING == self.identifier or OUTPUT_STRING == self.identifier
        second = len(self.terms) == 1 or len(self.terms) == 2
        return first and second

    def __iter__(self):
        return iter(self.terms[:])

    def __str__(self):
        result = ""
        if self.negated:
            result += "not "
        result += self.identifier
        if len(self.terms) > 0:
            result = result + "(" + ",".join(str(term) for term in self.terms) + ")"
        return result

    def get_placemarkers_1(self, result):
        if result is None:
            raise ValueError(f"Illegal 'result' argument in Scheme.get_placemarkers(result): {result}")
        for term in self.terms:
            if term.is_placemarker():
                result.add(term)
            elif isinstance(term, Scheme):
                term.get_placemarkers_1(result)

    placemarkers = None

    def has_placemarkers(self):
        return len(self.get_placemarkers_0()) > 0

    def get_placemarkers_0(self):
        if self.placemarkers is None:
            result = LinkedHashSet()
            self.get_placemarkers_1(result)
            self.placemarkers = list(result)
        return self.placemarkers

    def has_types(self):
        return len(self.get_placemarkers_0()) > 0

    def get_types(self):
        length = len(self.get_placemarkers_0())
        result = []
        for i in range(length):
            result.append(f"{self.placemarkers[i].get_identifier()}(V{i + 1})")
        return result

    def get_variables(self, *args):
        length = len(self.get_placemarkers_0())
        result = []
        for i in range(length):
            result.append(f"V{i + 1}")
        return result

    def matches(self, candidate):
        if candidate is None:
            raise ValueError("Illegal 'candidate' argument in Scheme.matches(Term): None")
        if not isinstance(candidate, Atom):
            return False
        atom = candidate
        if atom.get_identifier() != self.identifier or atom.get_arity() != len(self.terms):
            return False

        result = True
        for i, term in enumerate(self.terms):
            if result:
                atom_term = atom.get_term(i)
                if isinstance(term, Number):
                    result = isinstance(atom_term, Number) and term == atom_term
                elif term.is_quotation():
                    result = atom_term.is_quotation() and term == atom_term
                elif term.is_placemarker():
                    result = True
                elif isinstance(term, Scheme):
                    result = term.matches(atom_term)
                else:
                    result = False
            else:
                break
        return result
































