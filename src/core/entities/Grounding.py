
from src.core import Utils
from src.core.Buildable import Buildable
from src.core.LinkedHashSet import LinkedHashSet
from src.core.terms.Atom import Atom
from src.core.terms.Literal import Literal
from src.core.parser.Parser import Parser
from src.core.terms.SchemeTerm import SchemeTerm
from src.core.terms.Clause import Clause
from src.core.Dialler import Dialler
from src.core.entities.Answer import Answer
from src.core.Logger_copy import Logger
from src.core.entities.Values import Values
from src.core.entities.Solvable import Solvable


class Grounding(Solvable):

    config = None
    count = 0
    covered = []
    delta = []
    facts = set()
    generalisation = None
    kernel = []
    model = []
    problem = None
    table = set()
    uncovered = []

    class Builder(Buildable):
        covered = set()
        delta = set()
        facts = set()
        model = set()
        problem = None
        uncovered = set()

        def __init__(self, problem):
            if problem is None:
                raise ValueError(f"Illegal 'builder' argument in Grounding.Builder(problem): {problem}")
            self.problem = problem

        def add_atom(self, atom):
            if atom is None:
                raise ValueError(f"Illegal 'builder' argument in Grounding.Builder.add_atom(atom): {atom}")
            identifier = atom.get_identifier()
            if identifier.startswith("abduced_"):
                delta = atom.get_identifier()[len("abduced_"):]
                self.delta.add(Atom.Builder(delta).add_terms(atom.get_terms()).build())
            else:
                if self.problem.get_config().is_full() and self.problem.has_displays() and self.problem.look_up(atom):
                    self.model.add(atom)
                self.facts.add(atom)
            return self

        def add_atoms(self, atoms):
            if atoms is None:
                raise ValueError(f"Illegal 'builder' argument in Grounding.Builder.add_atoms(atoms): {atoms}")
            for atom in atoms:
                self.add_atom(atom)
            return self

        def build(self):
            self.covered.clear()
            self.uncovered.clear()
            for example in self.problem.get_examples():
                atom = example.get_atom()
                if example.is_negated() is not (atom in self.facts):
                    self.covered.add(Literal.Builder(atom).set_negated(example.is_negated()).build())
                else:
                    self.uncovered.add(Literal.Builder(atom).set_negated(example.is_negated()).build())
            return Grounding(self)

        def clear(self):
            self.covered.clear()
            self.delta.clear()
            self.facts.clear()
            self.model.clear()
            self.uncovered.clear()
            return self

        def parse(self, answer):
            if answer is None:
                raise ValueError(f"Illegal 'builder' argument in Grounding.Builder.parse(answer): {answer}")
            for atom in answer:
                self.add_atom(Parser.parse_token(atom))
            return self

        def remove_atom(self, atom):
            if atom is None:
                raise ValueError(f"Illegal 'builder' argument in Grounding.Builder.remove_atom(atom): {atom}")
            if atom.get_identifier().startswith("abduced_"):
                self.delta.remove(Atom.Builder(atom.get_identifier()[len("abduced_")]).add_terms(atom.get_terms()).build())
            else:
                if self.problem.get_config().is_full() and self.problem.has_displays() and self.problem.look_up(atom):
                    self.model.remove(atom)
                self.facts.remove(atom)
            return self

        def remove_atoms(self, atoms):
            if atoms is None:
                raise ValueError(f"Illegal 'builder' argument in Grounding.Builder.remove_atoms(atoms): {atoms}")
            for atom in atoms:
                self.remove_atom(atom)
            return self

    def is_problem(self):
        return False

    def __init__(self, builder):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Grounding(builder): {builder}")
        self.config = builder.problem.get_config()
        self.problem = builder.problem
        self.count = len(builder.delta)
        self.covered = list(builder.covered)
        self.delta = list(builder.delta)
        self.facts = builder.facts
        self.model = list(builder.model)
        self.uncovered = list(builder.uncovered)
        self.table = SchemeTerm.look_up(builder.problem.get_modeHs(), builder.problem.get_modeBs(), builder.facts)

    def as_bad_solution(self):
        delta_str = ", ".join(str(atom) for atom in self.delta) + "," if self.count > 0 else ""
        result = f"bad_solution:-{delta_str}number_abduced({self.count})."

        return result

    def as_clauses(self):
        result = LinkedHashSet()
        clauses = self.get_generalisation()
        if clauses:
            result.add("{ use_clause_literal(V1,0) }:-clause(V1).")

            has_literals = any(len(clause.get_body()) > 0 for clause in clauses)

            if has_literals:
                result.add("{ use_clause_literal(V1,V2) }:-clause(V1),literal(V1,V2).")

            for clause_id, clause in enumerate(clauses):
                result.add(f"%% {clause}")
                literals = clause.get_body()
                result.add(f"clause({clause_id}).")
                for literal_id, _ in enumerate(literals, start=1):
                    result.add(f"literal({clause_id},{literal_id}).")

                for level in range(clause.get_levels()):
                    result.add(f":-not clause_level({clause_id},{level}),clause_level({clause_id},{level + 1}).")

                result.add(f"clause_level({clause_id},0):-use_clause_literal({clause_id},0).")
                for literal_id, literal in enumerate(literals, start=1):
                    result.add(f"clause_level({clause_id},{literal.get_level()}):-use_clause_literal({clause_id},{literal_id}).")

                head = clause.get_head()
                result.add(f"#minimize{{ {head.get_weight()} @{head.get_priority()} : use_clause_literal({clause_id},0) }}.")
                for literal_id, literal in enumerate(literals, start=1):
                    result.add(f"#minimize{{ {literal.get_weight()} @{literal.get_priority()} : use_clause_literal({clause_id},{literal_id}) }}.")

                types_set = {type_ for literal in [head] + list(literals) for type_ in literal.get_types()}
                types_all = ",".join(types_set)
                literals_all = ",".join(f"try_clause_literal({clause_id},{literal_id}{','.join(literal.get_variables())})" for literal_id, literal in enumerate(literals, start=1))
                result.add(f"{head}:-use_clause_literal({clause_id},0), {literals_all}{types_all}.")

                for literal_id, literal in enumerate(literals, start=1):
                    variables = ",".join(literal.get_variables())
                    types = ",".join(literal.get_types())
                    result.add(f"try_clause_literal({clause_id},{literal_id}{variables}):-use_clause_literal({clause_id},{literal_id}),{literal}{types}.")
                    result.add(f"try_clause_literal({clause_id},{literal_id}{variables}):-not use_clause_literal({clause_id},{literal_id}){types}.")

        return list(result)

    def __eq__(self, other):
        if not isinstance(other, Grounding):
            return False
        if self is other:
            return True
        return (self.covered == other.covered and
                self.delta == other.delta and
                self.facts == other.facts and
                self.generalisation == other.generalisation and
                self.kernel == other.kernel and
                self.model == other.model and
                self.table == other.table and
                self.problem == other.problem and
                self.uncovered == other.uncovered)

    def get_background(self): return self.problem.get_background()

    def get_config(self): return self.config

    def get_count(self): return self.count

    def get_covered(self): return self.covered

    def get_delta(self): return self.delta

    def get_displays(self): return self.problem.get_displays()

    def get_domains(self): return self.problem.get_domains()

    def get_examples(self): return self.problem.get_examples()

    def get_facts(self): return self.facts

    def get_filters(self):
        result = set()
        # result.add("#hide.")
        # 可以按需取消注释下面的行
        # result.add("#show display_fact/1.")
        # result.add("#show covered_example/2.")
        # result.add("#show number_abduced/1.")
        # result.add("#show uncovered_example/2.")
        result.add("#show use_clause_literal/2.")
        for display in self.problem.get_displays():
            result.add(f"#show {display.get_identifier()}/{display.get_arity()}.")
        for example in self.problem.get_examples():
            result.add(f"#show {example.get_atom().get_identifier()}/{example.get_atom().get_arity()}.")
        return result

    def get_generalisation(self):
        if self.generalisation is None:
            set_of_clauses = LinkedHashSet()
            for clause in self.get_kernel():
                substitution_map = {}
                builder = Clause.Builder()
                head_atom = clause.get_head()
                for modeH in self.problem.get_modeHs():
                    if SchemeTerm.subsumes(modeH.scheme, head_atom, self.facts):
                        builder.set_head(modeH.scheme.generalises(head_atom, substitution_map))
                for literal in clause.get_body():
                    body_atom = literal.get_atom()
                    for modeB in self.problem.get_modeBs():
                        if SchemeTerm.subsumes(modeB.scheme, body_atom, self.facts):
                            generalized_atom = modeB.scheme.generalises(body_atom, substitution_map)
                            builder.add_literal(Literal.Builder(generalized_atom)
                                                .set_negated(literal.is_negated())
                                                .set_level(literal.get_level())
                                                .build())
                set_of_clauses.add(builder.build())
            self.generalisation = list(set_of_clauses)
        return self.generalisation

    def get_kernel(self):
        if self.generalisation is None:
            self.kernel = []
            sets =  LinkedHashSet()
            for alpha in self.delta:
                for modeH in self.problem.modeHs:
                    scheme = modeH.scheme
                    if SchemeTerm.subsumes(scheme, alpha, self.facts):
                        # head = Atom(alpha.identifier, alpha.terms, modeH.weight, modeH.priority)
                        builder = Clause.Builder().set_head(
                            Atom.Builder(alpha).set_weight(modeH.get_weight()).set_priority(modeH.get_priority()).build()
                        )
                        substitutes = SchemeTerm.find_substitutes(scheme, alpha)

                        if substitutes is not None:
                            usables = set(substitutes)
                            used = set()
                            next_usables = set()

                            level = 0
                            while usables:
                                level += 1
                                for modeB in self.problem.modeBs:
                                    scheme = modeB.get_scheme()
                                    if modeB.is_negated:
                                        found = SchemeTerm.generate_and_output_4(scheme, usables, self.table, self.facts)
                                        for atom, terms in found.items():
                                            builder.add_literal(Literal.Builder(Atom.Builder(atom).set_weight(modeB.get_weight()).set_priority(modeB.get_priority()).build()).set_negated(modeB.is_negated).set_level(level).build())
                                            next_usables.update(terms)
                                    else:
                                        matches = SchemeTerm.match_and_output(scheme, self.problem.table.get(scheme), usables)
                                        for atom in matches[0]:
                                            builder.add_literal(Literal.Builder(Atom.Builder(atom).set_weight(modeB.get_weight()).set_priority(modeB.get_priority()).build()).set_negated(modeB.is_negated).set_level(level).build())
                                        next_usables.update(matches[1])

                                used.update(usables)
                                next_usables.difference_update(used)
                                usables = next_usables
                                next_usables = set()

                        sets.add(builder.build())
            self.kernel = list(sets)            # self.kernel.append(builder.build())
        return self.kernel

    def get_modeBs(self): return self.problem.get_modeBs()
    def get_modeHs(self): return self.problem.get_modeHs()
    def get_model(self): return self.model
    def get_problem(self): return self.problem
    def get_table(self): return self.table
    def get_uncovered(self): return self.uncovered
    def has_background(self): return self.problem.has_background()
    def has_covered(self): return len(self.covered) > 0
    def has_delta(self): return len(self.delta) > 0
    def has_displays(self): return self.problem.has_displays()
    def has_domains(self): return len(self.problem.get_domains()) > 0
    def has_examples(self): return self.problem.has_examples()
    def has_generalisation(self): return len(self.generalisation) > 0

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + hash(tuple(self.covered))
        result = prime * result + hash(tuple(self.delta))
        result = prime * result + (hash(frozenset(self.facts)) if self.facts is not None else 0)
        result = prime * result + hash(tuple(self.generalisation))
        result = prime * result + hash(tuple(self.kernel))
        result = prime * result + hash(tuple(self.model))
        result = prime * result + (hash(tuple(self.table)) if self.table is not None else 0)
        result = prime * result + (hash(self.problem) if self.problem is not None else 0)
        result = prime * result + hash(tuple(self.uncovered))
        return result

    def has_kernel(self): return len(self.get_kernel()) > 0
    def has_model(self): return len(self.model) > 0
    def has_modes(self): return self.problem.has_modes()
    def has_uncovered(self): return len(self.uncovered) > 0

    def look_up(self, atom):
        if atom is None:
            raise ValueError(f"Illegal 'atom' argument in Grounding.look_up(atom): {atom}")
        return self.problem.look_up(atom)

    def needs_induction(self):
        return len(self.get_generalisation()) > 0

    def save(self, iteration, file_path):
        with open(file_path, 'a') as file:
            return Utils.save(self, iteration, file)

    def solve(self, values, builder):
        from src.core.entities.Answers import Answers
        if values is None:
            raise ValueError("Illegal 'values' argument in Grounding.solve: values cannot be None")
        if builder is None:
            raise ValueError("Illegal 'builder' argument in Grounding.solve: builder cannot be None")

        result = values
        if self.needs_induction():
            dialler = Dialler.Builder(self.config).add_grounding(self).add_values(values).build()
            entry = Answers.time_induction(1, dialler)
            keys = entry.keys()
            result = Values(keys)
            for var10 in entry.values():
                for output in var10:
                    if builder.size() > 0 and self.config.is_terminate():
                        break
                    hypothesis = Answers.time_deduction(self, output)
                    if self.config.is_debug:
                        print(f"*** Info ({Logger.SIGNATURE}): found Hypothesis: {', '.join([str(h) for h in hypothesis.hypotheses])}")
                    builder.put(result, Answer.Builder(self).set_hypothesis(hypothesis).build())
        else:
            builder.put(Values(), Answer.Builder(self).build())

        return result


    def __str__(self):
        return (f"Grounding [\n"
                f"  covered={self.covered},\n"
                f"  delta={self.delta},\n"
                f"  facts={self.facts},\n"
                f"  generalisation={self.generalisation},\n"
                f"  kernel={self.kernel},\n"
                f"  model={self.model},\n"
                f"  table={self.table},\n"
                f"  problem={self.problem},\n"
                f"  uncovered={self.uncovered}\n"
                "]")

























# from sortedcontainers import SortedSet
#
# from src.core import Utils
# from src.core.Buildable import Buildable
# from src.core.terms.Atom import Atom
# from src.core.terms.Literal import Literal
# from src.core.parser.Parser import Parser
# from src.core.terms.SchemeTerm import SchemeTerm
# from src.core.terms.Clause import Clause
# from src.core.Dialler import Dialler
# from src.core.entities.Answers import Answers
# from src.core.entities.Answer import Answer
# from src.core.Logger import Logger
# from src.core.entities.Values import Values
# from src.core.entities.Solvable import Solvable
#
#
# class Grounding(Solvable):
#
#     config = None
#     count = 0
#     covered = []
#     delta = []
#     facts = set()
#     generalisation = None
#     kernel = []
#     model = []
#     problem = None
#     table = set()
#     uncovered = []
#
#     class Builder(Buildable):
#         covered = set()
#         delta = set()
#         facts = set()
#         model = set()
#         problem = None
#         uncovered = set()
#
#         def __init__(self, problem):
#             if problem is None:
#                 raise ValueError(f"Illegal 'builder' argument in Grounding.Builder(problem): {problem}")
#             self.problem = problem
#
#         def add_atom(self, atom):
#             if atom is None:
#                 raise ValueError(f"Illegal 'builder' argument in Grounding.Builder.add_atom(atom): {atom}")
#             if atom.get_identifier.startswith("abduced_"):
#                 self.delta.add(Atom.Builder(atom.get_identifier()[len("abduced_")]).add_terms(atom.get_terms).build())
#             else:
#                 if self.problem.get_config().is_full() and self.problem.has_displays() and self.problem.look_up(atom):
#                     self.model.add(atom)
#                 self.facts.add(atom)
#             return self
#
#         def add_atoms(self, atoms):
#             if atoms is None:
#                 raise ValueError(f"Illegal 'builder' argument in Grounding.Builder.add_atoms(atoms): {atoms}")
#             for atom in atoms:
#                 self.add_atom(atom)
#             return self
#
#         def build(self):
#             self.covered.clear()
#             self.uncovered.clear()
#             for example in self.problem.get_examples():
#                 atom = example.get_atom
#                 if example.is_negated() is not (atom in self.facts):
#                     self.covered.add(Literal.Builder(atom).set_negated(example.is_negated()).build())
#                 else:
#                     self.uncovered.add(Literal.Builder(atom).set_negated(example.is_negated()).build())
#             return Grounding(self)
#
#         def clear(self):
#             self.covered.clear()
#             self.delta.clear()
#             self.facts.clear()
#             self.model.clear()
#             self.uncovered.clear()
#             return self
#
#         def parse(self, answer):
#             if answer is None:
#                 raise ValueError(f"Illegal 'builder' argument in Grounding.Builder.parse(answer): {answer}")
#             for atom in answer:
#                 self.add_atom(Parser.parse_token(atom))
#             return self
#
#         def remove_atom(self, atom):
#             if atom is None:
#                 raise ValueError(f"Illegal 'builder' argument in Grounding.Builder.remove_atom(atom): {atom}")
#             if atom.get_identifier().startswith("abduced_"):
#                 self.delta.remove(Atom.Builder(atom.get_identifier()[len("abduced_")]).add_terms(atom.get_terms()).build())
#             else:
#                 if self.problem.get_config().is_full() and self.problem.has_displays() and self.problem.look_up(atom):
#                     self.model.remove(atom)
#                 self.facts.remove(atom)
#             return self
#
#         def remove_atoms(self, atoms):
#             if atoms is None:
#                 raise ValueError(f"Illegal 'builder' argument in Grounding.Builder.remove_atoms(atoms): {atoms}")
#             for atom in atoms:
#                 self.remove_atom(atom)
#             return self
#
#     def is_problem(self):
#         return False
#
#     def __init__(self, builder):
#         if builder is None:
#             raise ValueError(f"Illegal 'builder' argument in Grounding(builder): {builder}")
#         self.config = builder.problem.get_config()
#         self.problem = builder.problem
#         self.count = len(builder.delta)
#         self.covered = list(builder.covered)
#         self.delta = list(builder.delta)
#         self.facts = builder.facts
#         self.model = list(builder.model)
#         self.uncovered = list(builder.uncovered)
#         self.table = SchemeTerm.look_up(builder.problem.get_modeHs, builder.problem.get_modeBs, builder.facts)
#
#     def as_bad_solution(self):
#         delta_str = ", ".join(str(atom) for atom in self.delta) + "," if self.count > 0 else ""
#         result = f"bad_solution:-{delta_str}number_abduced({self.count})."
#
#         return result
#
#     def as_clauses(self):
#         result = set()
#         clauses = self.get_generalisation()
#         if clauses:
#             result.add("{ use_clause_literal(V1,0) }:-clause(V1).")
#
#             has_literals = any(len(clause.get_body()) > 0 for clause in clauses)
#
#             if has_literals:
#                 result.add("{ use_clause_literal(V1,V2) }:-clause(V1),literal(V1,V2).")
#
#             for clause_id, clause in enumerate(clauses):
#                 result.add(f"%% {clause}")
#                 literals = clause.get_body()
#                 result.add(f"clause({clause_id}).")
#                 for literal_id, _ in enumerate(literals, start=1):
#                     result.add(f"literal({clause_id},{literal_id}).")
#
#                 for level in range(clause.get_levels()):
#                     result.add(f":-not clause_level({clause_id},{level}),clause_level({clause_id},{level + 1}).")
#
#                 result.add(f"clause_level({clause_id},0):-use_clause_literal({clause_id},0).")
#                 for literal_id, literal in enumerate(literals, start=1):
#                     result.add(f"clause_level({clause_id},{literal.get_level()}):-use_clause_literal({clause_id},{literal_id}).")
#
#                 head = clause.get_head()
#                 result.add(f"#minimize[ use_clause_literal({clause_id},0) ={head.get_weight()} @{head.get_priority()} ].")
#                 for literal_id, literal in enumerate(literals, start=1):
#                     result.add(f"#minimize[ use_clause_literal({clause_id},{literal_id}) ={literal.get_weight()} @{literal.get_priority()} ].")
#
#                 types_set = {type_ for literal in [head] + list(literals) for type_ in literal.get_types()}
#                 types_all = ",".join(types_set)
#                 literals_all = ",".join(f"try_clause_literal({clause_id},{literal_id}{','.join(literal.get_variables())})" for literal_id, literal in enumerate(literals, start=1))
#                 result.add(f"{head}:-use_clause_literal({clause_id},0){literals_all},{types_all}.")
#
#                 for literal_id, literal in enumerate(literals, start=1):
#                     variables = ",".join(literal.get_variables())
#                     types = ",".join(literal.get_types())
#                     result.add(f"try_clause_literal({clause_id},{literal_id}{variables}):-use_clause_literal({clause_id},{literal_id}),{literal}{types}.")
#                     result.add(f"try_clause_literal({clause_id},{literal_id}{variables}):-not use_clause_literal({clause_id},{literal_id}){types}.")
#
#         return list(result)
#
#     def __eq__(self, other):
#         if not isinstance(other, Grounding):
#             return False
#         if self is other:
#             return True
#         return (self.covered == other.covered and
#                 self.delta == other.delta and
#                 self.facts == other.facts and
#                 self.generalisation == other.generalisation and
#                 self.kernel == other.kernel and
#                 self.model == other.model and
#                 self.table == other.table and
#                 self.problem == other.problem and
#                 self.uncovered == other.uncovered)
#
#     def get_background(self): return self.problem.get_background()
#
#     def get_config(self): return self.config
#
#     def get_count(self): return self.count
#
#     def get_covered(self): return self.covered
#
#     def get_delta(self): return self.delta
#
#     def get_displays(self): return self.problem.get_displays()
#
#     def get_domains(self): return self.problem.get_domains()
#
#     def get_examples(self): return self.problem.get_examples()
#
#     def get_facts(self): return self.facts
#
#     def get_filters(self):
#         result = SortedSet()
#         result.add("#hide.")
#         # 可以按需取消注释下面的行
#         # result.add("#show display_fact/1.")
#         # result.add("#show covered_example/2.")
#         # result.add("#show number_abduced/1.")
#         # result.add("#show uncovered_example/2.")
#         result.add("#show use_clause_literal/2.")
#         for display in self.problem.get_displays():
#             result.add(f"#show {display.identifier}/{display.arity}.")
#         for example in self.problem.get_examples():
#             result.add(f"#show {example.atom.identifier}/{example.atom.arity}.")
#         return result
#
#     def get_generalisation(self):
#         if self.generalisation is None:
#             set_of_clauses = set()
#             for clause in self.get_kernel():
#                 substitution_map = {}
#                 builder = Clause.Builder()
#                 head_atom = clause.get_head()
#                 for modeH in self.problem.get_modeHs():
#                     if SchemeTerm.subsumes(modeH.scheme, head_atom, self.facts):
#                         builder.set_head(modeH.scheme.generalise(head_atom, substitution_map))
#                 for literal in clause.get_body():
#                     body_atom = literal.get_atom()
#                     for modeB in self.problem.get_modeBs():
#                         if SchemeTerm.subsumes(modeB.scheme, body_atom, self.facts):
#                             generalized_atom = modeB.scheme.generalise(body_atom, substitution_map)
#                             builder.add_literal(Literal.Builder(generalized_atom)
#                                                 .set_negated(literal.is_negated())
#                                                 .set_level(literal.get_level())
#                                                 .build())
#                 set_of_clauses.add(builder.build())
#             self.generalisation = list(set_of_clauses)
#         return self.generalisation
#
#     def get_kernel(self):
#         if self.generalisation is None:
#             self.kernel = []
#             for alpha in self.delta:
#                 for modeH in self.problem.modeHs:
#                     scheme = modeH.scheme
#                     if SchemeTerm.subsumes(scheme, alpha, self.problem.facts):
#                         # head = Atom(alpha.identifier, alpha.terms, modeH.weight, modeH.priority)
#                         builder = Clause.Builder().set_head(
#                             Atom.Builder(alpha).set_weight(modeH.get_weight()).set_priority(modeH.get_priority().build())
#                         )
#                         substitutes = SchemeTerm.find_substitutes(scheme, alpha)
#
#                         if substitutes:
#                             usables = set(substitutes)
#                             used = set()
#                             next_usables = set()
#
#                             level = 0
#                             while usables:
#                                 level += 1
#                                 for modeB in self.problem.modeBs:
#                                     scheme = modeB.scheme
#                                     if modeB.is_negated:
#                                         found = SchemeTerm.generate_and_output_4(scheme, usables, self.problem.table, self.problem.facts)
#                                         for atom, terms in found.items():
#                                             builder.add_literal(Literal.Builder(Atom.Builder(atom).set_weight(modeB.get_weight()).set_priority(modeB.get_priority()).build()).set_negated(modeB.is_negated).set_level(level).build())
#                                             next_usables.update(terms)
#                                     else:
#                                         matches = SchemeTerm.match_and_output(scheme, self.problem.table.get(scheme), usables)
#                                         for atom in matches[0]:
#                                             builder.add_literal(Literal.Builder(Atom.Builder(atom).set_weight(modeB.get_weight()).set_priority(modeB.get_priority()).build()).set_negated(modeB.is_negated).set_level(level).build())
#                                         next_usables.update(matches[1])
#
#                                 used.update(usables)
#                                 next_usables.difference_update(used)
#                                 usables = next_usables
#                                 next_usables = set()
#
#                             self.kernel.append(builder.build)
#         return self.kernel
#
#     def get_modeBs(self): return self.problem.get_modeBs()
#     def get_modeHs(self): return self.problem.get_modeHs()
#     def get_model(self): return self.model
#     def get_problem(self): return self.problem
#     def get_table(self): return self.table
#     def get_uncovered(self): return self.uncovered
#     def has_background(self): return self.problem.has_background()
#     def has_covered(self): return len(self.covered) > 0
#     def has_delta(self): return len(self.delta) > 0
#     def has_displays(self): return self.problem.has_displays()
#     def has_domains(self): return len(self.problem.get_domains()) > 0
#     def has_examples(self): return self.problem.has_examples()
#     def has_generalisation(self): return len(self.generalisation) > 0
#
#     def __hash__(self):
#         prime = 31
#         result = 1
#         result = prime * result + hash(tuple(self.covered))
#         result = prime * result + hash(tuple(self.delta))
#         result = prime * result + (hash(frozenset(self.facts)) if self.facts is not None else 0)
#         result = prime * result + hash(tuple(self.generalisation))
#         result = prime * result + hash(tuple(self.kernel))
#         result = prime * result + hash(tuple(self.model))
#         result = prime * result + (hash(self.table) if self.table is not None else 0)
#         result = prime * result + (hash(self.problem) if self.problem is not None else 0)
#         result = prime * result + hash(tuple(self.uncovered))
#         return result
#
#     def has_kernel(self): return len(self.get_kernel()) > 0
#     def has_model(self): return len(self.model) > 0
#     def has_modes(self): return self.problem.has_modes()
#     def has_uncovered(self): return len(self.uncovered) > 0
#
#     def look_up(self, atom):
#         if atom is None:
#             raise ValueError(f"Illegal 'atom' argument in Grounding.look_up(atom): {atom}")
#         return self.problem.look_up(atom)
#
#     def needs_induction(self):
#         return len(self.get_generalisation()) > 0
#
#     def save(self, iteration, file_path):
#         with open(file_path, 'a') as file:
#             return Utils.save(self, iteration, file)
#
#     def solve(self, values, builder):
#         if values is None:
#             raise ValueError("Illegal 'values' argument in Grounding.solve: values cannot be None")
#         if builder is None:
#             raise ValueError("Illegal 'builder' argument in Grounding.solve: builder cannot be None")
#
#         result = values
#         if self.needs_induction():
#             dialler = Dialler.Builder(self.config, self, values).build()
#             entry = Answers.time_induction(1, dialler)
#             result = entry[0]  # entry.getKey() in Java corresponds to entry[0] in Python
#
#             for output in entry[1]:  # entry.getValue() in Java corresponds to entry[1] in Python
#                 if builder.size() > 0 and self.config.is_terminate:
#                     break
#                 hypothesis = Answers.time_deduction(self, output)
#                 if self.config.is_debug:
#                     print(f"*** Info ({Logger.SIGNATURE}): found Hypothesis: {', '.join([str(h) for h in hypothesis.hypotheses])}")
#                 builder.put(result, Answer.Builder(self).set_hypothesis(hypothesis).build())
#         else:
#             builder.put(Values(), Answer.Builder(self).build())
#
#         return result
#
#     def __str__(self):
#         return (f"Grounding [\n"
#                 f"  covered={self.covered},\n"
#                 f"  delta={self.delta},\n"
#                 f"  facts={self.facts},\n"
#                 f"  generalisation={self.generalisation},\n"
#                 f"  kernel={self.kernel},\n"
#                 f"  model={self.model},\n"
#                 f"  table={self.table},\n"
#                 f"  problem={self.problem},\n"
#                 f"  uncovered={self.uncovered}\n"
#                 "]")
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
