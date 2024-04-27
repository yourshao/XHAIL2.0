# from src.core.Buildable import Buildable
#
# class ModeH():
#
#     class Builder(Buildable):
#
#         lower = 0
#         priority = 0
#         scheme = None
#         upper = float('inf')
#
#         weight = 1
#
#         def __init__(self, scheme):
#             if scheme is None:
#                 raise ValueError(f"Illegal 'scheme' argument in ModeH.Builder(scheme): {scheme}")
#             self.scheme = scheme
#
#         COUNT = 0
#
#         def build(self):
#             self.COUNT += 1
#             return ModeH(self, self.COUNT)
#
#         def set_lower(self, lower):
#             self.lower = lower
#             return self
#
#         def set_priority(self, priority):
#             self.priority = priority
#             return self
#
#         def set_scheme(self, scheme):
#             if scheme is None:
#                 raise ValueError(f"Illegal 'scheme' argument in ModeH.Builder.set_scheme(scheme): {scheme}")
#             else:
#                 self.scheme = scheme
#             return self
#
#         def set_upper(self, upper):
#             self.upper = upper
#             return self
#
#         def set_weight(self, weight):
#             self.weight = 1 if weight is None else weight
#
#     CONSTRAINT_OP = ":"
#     KEYWORD = "#modeh"
#     PRIORITY_OP = "@"
#     SEPARATOR_OP = "-"
#     WEIGHT_OP = "="
#
#     lower = None
#     priority = None
#     scheme = None
#     upper = None
#     weight = None
#     id = None
#
#     def __init__(self, builder, id):
#         self.lower = builder.lower
#         self.priority = builder.priority
#         self.scheme = builder.scheme
#         self.upper = builder.upper
#         self.weight = builder.weight
#         self.id = id
#
#     # 这里是不稳定的， 据说不应该出现unsafe的情况
#     def as_clause(self):
#         varss = set()  # Using a Python set for variable storage
#         atom = str(self.scheme.generalises(varss))  # Assume generalises returns an Atom object
#         types = " :" + " :".join(self.scheme.get_types()) if len(self.scheme.get_types()) > 0 else ""
#         lists = "," + ",".join(self.scheme.get_types()) if len(self.scheme.get_types()) > 0 else ""
#
#         result = [None] * 5
#         result[0] = f"%% {self}"
#         result[1] = f"{self.lower} {{ abduced_{atom}{types} }} {self.upper}."
#         result[2] = f"#minimize{{ {self.weight}@{self.priority}{types}, abduced_{atom} }}."
#         result[3] = f"{atom}:-abduced_{atom}{lists}."
#         result[4] = f"number_abduced({self.id},V):-V:=#count{{ abduced_{atom}{types} }}."
#         return result
#
#
#     #
#     # def as_clause(self):
#     #     varss = set()  # Using a Python set for variable storage
#     #     atom = str(self.scheme.generalises(varss))  # Assume generalises returns an Atom object
#     #     types = " :" + " :".join(self.scheme.get_types()) if len(self.scheme.get_types()) > 0 else ""
#     #     lists = "," + ",".join(self.scheme.get_types()) if len(self.scheme.get_types()) > 0 else ""
#     #
#     #     result = [None] * 5
#     #     result[0] = f"%% {self}"
#     #     result[1] = f"{self.lower} {{ abduced_{atom}{types} }} {self.upper}."
#     #     result[2] = f"#minimize{{ abduced_{atom} ={self.weight} @{self.priority}{types} }}."
#     #     result[3] = f"{atom}:-abduced_{atom}{lists}."
#     #     result[4] = f"number_abduced({self.id},V):-V:=#count{{ abduced_{atom}{types} }}."
#     #     return result
#
#
#
#
#     def __eq__(self, other):
#         if self is other:
#             return True
#         if not isinstance(other, ModeH):
#             return False
#         return (self.lower == other.lower and
#                 self.priority == other.priority and
#                 self.scheme == other.scheme and
#                 self.upper == other.upper and
#                 self.weight == other.weight)
#
#     def get_lower(self):
#         return self.lower
#
#     def get_priority(self):
#         return self.priority
#
#     def get_scheme(self):
#         return self.scheme
#
#     def get_upper(self):
#         return self.upper
#
#     def get_weight(self):
#         return self.weight
#
#     def __hash__(self):
#         prime = 31
#         result = 1
#         result = prime * result + self.lower
#         result = prime * result + self.priority
#         if self.scheme is None:
#             result = prime * result
#         else:
#             result = prime * result + hash(self.scheme)
#         result = prime * result + self.weight
#         return result
#
#     def __str__(self):
#         result = "modeh"
#         result += " " + str(self.scheme)
#         if self.lower != 0 or self.upper != float('inf'):
#             result += " :{}-{}".format(self.lower, int(self.upper) if self.upper != float('inf') else "inf")
#         if self.weight != 1:
#             result += " ={}".format(self.weight)
#         if self.priority != 1:
#             result += " @{}".format(self.priority)
#         result += "."
#         return result
#
#
from src.core.Buildable import Buildable

class ModeH():

    class Builder(Buildable):

        lower = 0
        priority = 0
        scheme = None
        upper = float('inf')

        weight = 1

        def __init__(self, scheme):
            if scheme is None:
                raise ValueError(f"Illegal 'scheme' argument in ModeH.Builder(scheme): {scheme}")
            self.scheme = scheme

        COUNT = 0

        def build(self):
            return ModeH(self, self.COUNT + 1)

        def set_lower(self, lower):
            self.lower = lower
            return self

        def set_priority(self, priority):
            self.priority = priority
            return self

        def set_scheme(self, scheme):
            if scheme is None:
                raise ValueError(f"Illegal 'scheme' argument in ModeH.Builder.set_scheme(scheme): {scheme}")
            self.scheme = scheme
            return self

        def set_upper(self, upper):
            self.upper = upper
            return self

        def set_weight(self, weight):
            self.weight = 1 if weight is None else weight

    CONSTRAINT_OP = ":"
    KEYWORD = "#modeh"
    PRIORITY_OP = "@"
    SEPARATOR_OP = "-"
    WEIGHT_OP = "="

    lower = None
    priority = None
    scheme = None
    upper = None
    weight = None
    id = None

    def __init__(self, builder, id):
        self.lower = builder.lower
        self.priority = builder.priority
        self.scheme = builder.scheme
        self.upper = builder.upper
        self.weight = builder.weight
        self.id = id

    # 这里是不稳定的， 据说不应该出现unsafe的情况
    def as_clauses(self):
        varss = set()  # Using a Python set for variable storage
        atom = str(self.scheme.generalises(varss))  # Assume generalises returns an Atom object
        types = " :" + " :".join(self.scheme.get_types()) if len(self.scheme.get_types()) > 0 else ""
        lists = "," + ",".join(self.scheme.get_types()) if len(self.scheme.get_types()) > 0 else ""

        result = [None] * 5
        result[0] = f"%% {self}"
        result[1] = f"{self.lower} {{ abduced_{atom}{types} }} {self.upper}."
        result[2] = f"#minimize{{ {self.weight}@{self.priority}{types}, abduced_{atom} }}."
        result[3] = f"{atom}:-abduced_{atom}{lists}."
        result[4] = f"number_abduced({self.id},V):-V:=#count{{ abduced_{atom}{types} }}."
        return result


    #
    # def as_clause(self):
    #     varss = set()  # Using a Python set for variable storage
    #     atom = str(self.scheme.generalises(varss))  # Assume generalises returns an Atom object
    #     types = " :" + " :".join(self.scheme.get_types()) if len(self.scheme.get_types()) > 0 else ""
    #     lists = "," + ",".join(self.scheme.get_types()) if len(self.scheme.get_types()) > 0 else ""
    #
    #     result = [None] * 5
    #     result[0] = f"%% {self}"
    #     result[1] = f"{self.lower} {{ abduced_{atom}{types} }} {self.upper}."
    #     result[2] = f"#minimize{{ abduced_{atom} ={self.weight} @{self.priority}{types} }}."
    #     result[3] = f"{atom}:-abduced_{atom}{lists}."
    #     result[4] = f"number_abduced({self.id},V):-V:=#count{{ abduced_{atom}{types} }}."
    #     return result




    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, ModeH):
            return False
        return (self.lower == other.lower and
                self.priority == other.priority and
                self.scheme == other.scheme and
                self.upper == other.upper and
                self.weight == other.weight)

    def get_lower(self):
        return self.lower

    def get_priority(self):
        return self.priority

    def get_scheme(self):
        return self.scheme

    def get_upper(self):
        return self.upper

    def get_weight(self):
        return self.weight

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + self.lower
        result = prime * result + self.priority
        if self.scheme is None:
            result = prime * result
        else:
            result = prime * result + hash(self.scheme)
        result = prime * result + self.weight
        return result

    def __str__(self):
        result = "modeh"
        result += " " + str(self.scheme)
        if self.lower != 0 or self.upper != float('inf'):
            result += " :{}-{}".format(self.lower, int(self.upper) if self.upper != float('inf') else "inf")
        if self.weight != 1:
            result += " ={}".format(self.weight)
        if self.priority != 1:
            result += " @{}".format(self.priority)
        result += "."
        return result


