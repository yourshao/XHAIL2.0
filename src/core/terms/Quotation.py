from src.core.terms.Term import Term
# from src.core.terms.SchemeTerm import SchemeTerm
from src.core.Buildable import Buildable


class Quotation(Term):

    class Builder(Buildable):

        content = None

        def __init__(self, content):
            if content is None:
                raise ValueError("Illegal 'content' argument in Quotation.__init__(String): None")
            content = content.strip()
            if len(content) < 2 or not content.startswith('"') or not content.endswith('"'):
                raise ValueError(f"Illegal 'content' argument in Quotation.__init__(String): {content}")
            self.content = content

        def build(self):
            return Quotation(self)

        def set_content(self, content):
            if content is None:
                raise ValueError("Illegal 'content' argument in Quotation.set_content(String): None")
            content = content.strip()
            if len(content) < 2 or not content.startswith('"') or not content.endswith('"'):
                raise ValueError(f"Illegal 'content' argument in Quotation.set_content(String): {content}")
            self.content = content
            return self


    content = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError("Illegal 'builder' argument in Quotation.__init__(Quotation.Builder): None")
        self.content = builder.content

    def __eq__(self, other):
        if not isinstance(other, Quotation):
            return False
        return self.content == other.content

    def generalises(self, *args):
        if len(args) == 1:
            set = args[0]
            if set is None:
                raise ValueError(f"Illegal 'set' argument in Quotation.generalises(Set<Variable>): {set}")
            return self
        elif len(args) == 2:
            term = args[0]
            map = args[1]
            if term is None:
                raise ValueError(f"Illegal 'term' argument in Quotation.generalises(Term, Map<Variable, Variable>): {term}")
            if map is None:
                raise ValueError(f"Illegal 'map' argument in Quotation.generalises(Term, Map<Variable, Variable>): {map}")
            if isinstance(term, Quotation):
                if term.get_content() == self.get_content():
                    return self
                else:
                    return None
            else:
                return None

    def get_content(self):
        return self.content

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (0 if self.content is None else hash(self.content))
        return result

    def __str__(self):
        return f"{self.content}"


    def is_quotation(self):
        return True



