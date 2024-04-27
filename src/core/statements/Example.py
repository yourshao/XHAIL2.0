from src.core.Buildable import Buildable

class Example:

    class Builder(Buildable):

        atom = None

        priority = 1
        negated = False
        weight = None

        def __init__(self, atom):
            if atom is None:
                raise ValueError(f"Illegal 'builder' argument in Example.Builder(atom): {atom}")
            self.atom = atom

        def build(self):
            return Example(self)

        def set_atom(self, atom):
            if atom is None:
                raise ValueError(f"Illegal 'builder' argument in Example.Builder.set_atom(atom): {atom}")
            self.atom = atom
            return self

        def set_negated(self, negated):
            self.negated = negated
            return self

        def set_priority(self, priority):
            self.priority = priority
            return self

        def set_weight(self, weight):
            self.weight = weight


    KEYWORD = "example"
    PRIORITY_OP = '@'
    WEIGHT_OP = '='
    defeasible = None
    atom = None
    priority = None
    weight = None
    negated = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Example(builder): {builder}")
        self.atom = builder.atom
        self.defeasible = self.weight is not None
        self.negated = builder.negated
        self.priority = builder.priority
        self.weight = 1 if builder.weight is None else builder.weight

    def __eq__(self, other):
        if not isinstance(other, Example):
            return False
        if self.atom != other.atom:
            return False
        if self.defeasible != other.defeasible:
            return False
        if self.negated != other.negated:
            return False
        if self.priority != other.priority:
            return False
        if self.weight != other.weight:
            return False
        return True

    def get_atom(self):
        return self.atom

    def get_priority(self):
        return self.priority

    def get_weight(self):
        return self.weight

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + 0 if self.atom is None else hash(self.atom)
        result = prime * result + 1231 if self.defeasible else 1237
        result = prime * result + 1231 if self.negated else 1237
        result = prime * result + self.priority
        result = prime * result + self.weight
        return result

    def is_defeasible(self):
        return self.defeasible

    def as_clauses(self):
        yes = "not " if self.negated else ""
        not_ = "" if self.negated else "not "
        result = [None] * (2 if self.defeasible else 3)
        # 删掉了百分号
        result[0] = f"%%{self}"
        result[1] = f"#maximize{{ {self.weight} @{self.priority} : {yes}{self.atom} }}."
        if not self.defeasible:
            result[2] = f":-{not_}{self.atom}."
        return result

    # def as_clauses(self):
    #     yes = "not " if self.negated else ""
    #     not_ = "" if self.negated else "not "
    #     result = [None] * (3 if self.defeasible else 4)
    #     # 删掉了百分号
    #     result[0] = f"%%{self}"
    #     result[1] = f"{self.atom}"
    #     result[2] = f"#maximize{{ {self.weight} @{self.priority} : {yes}{self.atom} }}."
    #     if not self.defeasible:
    #         result[3] = f":-{not_}{self.atom}."
    #     return result



    def is_negated(self):
        return self.negated

    def __str__(self):
        result = self.KEYWORD
        if self.negated:
            result += " not"
        result += " " + str(self.atom)
        if self.weight != 1:
            result += " " + self.WEIGHT_OP + str(self.weight)
        if self.priority != 1:
            result += " " + self.PRIORITY_OP + str(self.priority)
        result += "."
        return result



