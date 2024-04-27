from src.core.Buildable import Buildable


class Literal:

    class Builder(Buildable):

        atom = None
        level = 0
        negated = False

        def __init__(self, atom):
            if atom is None:
                raise ValueError(f"Illegal 'atom' argument in Literal.Builder(atom): {atom}")
            self.atom = atom

        def build(self):
            return Literal(self)

        def set_atom(self, atom):
            if atom is None:
                raise ValueError(f"Illegal 'atom' argument in Literal.Builder.set_atom(atom): {atom}")
            self.atom = atom
            return self

        def set_level(self, level):
            if level < 0:
                raise ValueError(f"Illegal 'level' argument in Literal.Builder.set_level(level): {level}")
            self.level = level
            return self

        def set_negated(self, negated):
            self.negated = negated
            return self

    atom = None
    level = None
    negated = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Literal(builder): {builder}")
        self.atom = builder.atom
        self.level = builder.level
        self.negated = builder.negated

    def compare_to(self, other):
        if self.atom < other.atom:
            return -1
        elif self.atom > other.atom:
            return 1
        else:
            if self.negated == other.negated:
                return 0
            elif self.negated and not other.negated:
                return 1
            else:
                return -1

    def __eq__(self, other):
        return self.compare_to(other) == 0

    def __lt__(self, other):
        return self.compare_to(other) < 0

    def equals(self, obj):
        return self.compare_to(obj) == 0

    def get_atom(self):
        return self.atom

    def get_level(self):
        return self.level

    def get_priority(self):
        return self.atom.get_priority()

    def get_scheme(self):
        return self.atom.get_scheme()

    def get_weight(self):
        return self.atom.get_weight()

    def __hash__(self):
        prime = 31
        result = 1
        # 哈希组合方式，如果atom是None，返回0，否则返回atom的哈希码
        result = prime * result + (hash(self.atom) if self.atom is not None else 0)
        # 加入level值的哈希
        result = prime * result + self.level
        # 为true和false分别使用不同的素数
        result = prime * result + (1231 if self.negated else 1237)
        return result

    def is_negated(self):
        return self.negated

    def __str__(self):
        return ("not " if self.negated else "") + str(self.atom)

    def has_variables(self):
        return self.atom.has_variables()

    def get_variables(self):
        return self.atom.get_variables()

    def has_types(self):
        return self.atom.has_types()

    def get_types(self):
        return self.atom.get_types()

