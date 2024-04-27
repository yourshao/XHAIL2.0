
from src.core.Buildable import Buildable


class Clause:

    class Builder(Buildable):

        body = set()
        head = None

        def __init__(self):
            self.body = set()
            self.head = None

        def add_literal(self, literal):
            if literal is None:
                raise ValueError(f"Illegal 'literal' argument in Clause.Builder.add_literal(literal): {literal}")
            self.body.add(literal)
            return self

        def add_literals(self, literals):
            if literals is None:
                raise ValueError(f"Illegal 'literals' argument in Clause.Builder.add_literals(literals): {literals}")
            for literal in literals:
                self.body.add(literal)
            return self

        def build(self):
            return Clause(self)

        def clear_body(self):
            self.body.clear()
            return self

        def remove_literal(self, literal):
            if literal is None:
                raise ValueError(f"Illegal 'literal' argument in Clause.Builder.remove_literal(literal): {literal}")
            self.body.remove(literal)
            return self

        def remove_literals(self, literals):
            if literals is None:
                raise ValueError(f"Illegal 'literals' argument in Clause.Builder.remove_literals(literals): {literals}")
            for literal in literals:
                self.body.remove(literal)
            return self

        def set_head(self, head):
            self.head = head
            return self

    body = None
    head = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Clause(builder): {builder}")
        new_body = list(builder.body)
        self.body = new_body
        self.head = builder.head

    def __eq__(self, other):
        if not isinstance(other, Clause):
            return False
        if self is other:
            return True
            # 比较 body，如果是列表，确保它们内容和顺序都相同
        if self.body != other.body:
            return False
            # 比较 head，这里直接使用 Python 的等号，它会调用 head 的 __eq__ 方法（如果有定义的话）
        if self.head != other.head:
            return False
        return True

    def get_body(self, *arge):
        if len(arge) == 0:
            return self.body
        elif len(arge) == 1:
            index = arge[0]
            if index < 1 or index > len(self.body):
                raise ValueError(f"Illegal 'index' argument in Clause.get_body(index): {index}")
            return self.body[index-1]

    def get_head(self):
        return self.head

    def get_size(self):
        return len(self.body)

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + hash(tuple(self.body))
        if self.head is not None:
            result = prime * result + hash(self.head)
        elif self.head is None:
            result = prime * result + 0
        return result

    def __iter__(self):
        return iter(self.body[:])

    def get_levels(self):
        result = 0
        for literal in self.body:
            result = max(result, literal.get_level())
        return result

    def __str__(self):
        result = ""
        if self.head is not None:
            result += str(self.head)  # 假设 head 对象有自己的 __str__ 方法
        if len(self.body) > 0 or self.head is None:
            result += ":-"
            for i, literal in enumerate(self.body):
                if i > 0:
                    result += ","
                result += str(literal)  # 假设每个 literal 也有自己的 __str__ 方法
        result += "."
        return result






