from src.core.Buildable import Buildable
from src.core.terms.Variable import Variable


class Atom:
    CONSTANT_STRING = "internal_const_par"
    INPUT_STRING = "internal_input_par"
    OUTPUT_STRING = "internal_output_par"

    class Builder(Buildable):

        def __str__(self):
            return (f"Builder [identifier={self.identifier}, terms={self.terms}, "
                    f"scheme={self.scheme}, weight={self.weight}, priority={self.priority}]")

        identifier = None
        priority = 1
        scheme = None
        terms = []
        weight = 1

        def __init__(self, atom_or_identifier):
            self.terms = []
            if isinstance(atom_or_identifier, str):
                atom_or_identifier = atom_or_identifier.strip()
                if atom_or_identifier is None or atom_or_identifier.strip() == "" or not ('a' <= atom_or_identifier.strip()[0] <= 'z'):
                    raise ValueError(f"Illegal 'atom' argument in Atom.Builder(atom): {atom_or_identifier}")
                self.identifier = atom_or_identifier
            elif isinstance(atom_or_identifier, Atom):
                if atom_or_identifier is None:
                    raise ValueError(f"Illegal 'atom' argument in Atom.Builder(atom): {atom_or_identifier}")
                self.identifier = atom_or_identifier.identifier
                self.priority = atom_or_identifier.priority
                self.scheme = atom_or_identifier.scheme
                # self.terms = []
                for term in atom_or_identifier.terms:
                    self.terms.append(term)
                self.weight = atom_or_identifier.weight
            else:
                raise ValueError(f"Illegal 'atom' argument in Atom.Builder(atom): {atom_or_identifier}")

        def add_term(self, term):
            if term is None:
                raise ValueError(f"Illegal 'term' argument in Atom.Builder.add_term(term): {term}")
            self.terms.append(term)
            return self

        def add_terms(self, terms):
            if terms is None:
                raise ValueError(f"Illegal 'terms' argument in Atom.Builder.add_terms(terms): {terms}")
            for term in terms:
                self.terms.append(term)
            return self

        def clear_terms(self):
            self.terms.clear()
            return self

        def build(self):
            return Atom(self)

        def clone(self):
            result = Atom.Builder(self.identifier).add_terms(self.terms).set_weight(self.weight).set_priority(self.priority)
            if self.scheme is not None:
                result.set_scheme(self.scheme)
            return result

        def remove_term(self, term):
            if term is None:
                raise ValueError(f"Illegal 'term' argument in Atom.Builder.remove_term(term): {term}")
            if term in self.terms:
                self.terms.remove(term)
            return self

        def remove_terms(self, terms):
            if terms is None:
                raise ValueError(f"Illegal 'terms' argument in Atom.Builder.remove_terms(terms): {terms}")
            for term in terms:
                if term in self.terms:
                    self.terms.remove(term)
            return self

        def set_identifier(self, identifier):
            identifier = identifier.strip()
            if identifier is None or identifier.strip() == "" or not ('a' <= identifier.strip()[0] <= 'z'):
                raise ValueError(f"Illegal 'identifier' argument in Atom.Builder.set_identifier(identifier): {identifier}")
            self.identifier = identifier
            return self

        def set_priority(self, priority):
            self.priority = priority
            return self

        def set_scheme(self, scheme):
            if scheme is None:
                raise ValueError(f"Illegal 'scheme' argument in Atom.Builder.set_scheme(scheme): {scheme}")
            self.scheme = scheme
            return self

        def set_weight(self, weight):
            self.weight = weight
            return self

    identifier = None
    priority = None
    scheme = None
    terms = None
    weight = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Atom(atom): {builder}")
        self.identifier = builder.identifier
        self.priority = builder.priority
        self.scheme = builder.scheme
        self.terms = []
        for term in builder.terms:
            self.terms.append(term)
        self.weight = builder.weight

    def compare_to(self, other):
        if other is None:
            return 1
            # 比较 identifier
        result = (self.identifier > other.identifier) - (self.identifier < other.identifier)
        if result == 0:
            # 比较 terms 长度
            result = len(self.terms) - len(other.terms)
            if result == 0:
                # 逐个比较 terms 元素
                for self_term, other_term in zip(self.terms, other.terms):
                    result = self_term.compare_to(other_term)  # 假设terms中元素实现了compare_to
                    if result != 0:
                        break
        return result

    def __lt__(self, other):
        return self.compare_to(other) < 0

    def __eq__(self, other):
        return self.compare_to(other) == 0

    def get_arity(self):
        return len(self.terms)

    def get_identifier(self):
        return self.identifier

    def get_priority(self):
        return self.priority

    def get_scheme(self):
        return self.scheme

    def get_term(self, index):
        return self.terms[index]

    def get_terms(self):
        return self.terms

    def get_weight(self):
        return self.weight

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + hash(self.identifier)
        result = prime * result + self.priority
        result = prime * result + hash(self.scheme)
        result = prime * result + hash(tuple(self.terms))
        result = prime * result + self.weight
        return result

    def is_placemarker(self):
        return ("CONSTANT_STRING" == self.identifier or
                "INPUT_STRING" == self.identifier or
                "OUTPUT_STRING" == self.identifier)

    def __iter__(self):
        return iter(self.terms[:])

    def __str__(self):
        result = self.identifier
        if len(self.terms) > 0:
            result += "("
            result += ",".join(str(term) for term in self.terms)
            result += ")"
        return result

    def get_variables(self, *args):
        if len(args) == 1:
            result = args[0]
            if result is None:
                raise ValueError("Illegal 'result' argument in Atom.get_variables(): " + str(result))
            for term in self.terms:
                if isinstance(term, Variable):
                    result.add(term)
                elif isinstance(term, Atom):
                    term.get_variables(result)
        elif len(args) == 0:
            if self.variables is None:
                result = set()
                self.get_variables(result)
                self.variables = list(result)
            return self.variables

    variables = None

    def has_variables(self):
        result = self.get_variables()
        return len(result) > 0

    def has_types(self):
        result = self.get_variables()
        return len(result) > 0

    def get_types(self):
        result = [f"{variable.get_type().getIdentifier()}({variable.get_identifier()})" for variable in self.get_variables()]
        return result




