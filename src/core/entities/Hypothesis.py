from src.core.Buildable import Buildable
from src.core.terms.Atom import Atom
from src.core.parser.Parser import Parser
from src.core.terms.Literal import Literal
from src.core.terms.Clause import Clause



class Hypothesis:

    class Builder(Buildable):

        covered = set()
        facts = set()
        grounding = None
        literals = set()
        model = set()

        uncovered = None

        def __init__(self, grounding):
            if grounding is None:
                raise ValueError(f"Illegal 'builder' argument in Hypothesis.Builder(grounding): {grounding}")
            self.grounding = grounding

        def add_atom(self, atom):
            if atom is None:
                raise ValueError(f"Illegal 'builder' argument in Hypothesis.Builder.add_atom(atom): {atom}")
            if (atom.get_identifier() == "use_clause_literal") and (2 == atom.get_arity()):
                self.literals.add(atom)
            else:
                if self.grounding.get_config().is_full() and self.grounding.has_displays() and self.grounding.look_up(atom):
                    self.model.add(atom)
                self.facts.add(atom)
            return self

        def add_atoms(self, atoms):
            if atoms is None:
                raise ValueError(f"Illegal 'builder' argument in Hypothesis.Builder.add_atoms(atoms): {atoms}")
            for atom in atoms:
                self.add_atom(atom)
            return self

        def build(self):
            self.covered = set()
            self.uncovered = set()
            for example in self.grounding.get_examples():
                atom = example.get_atom()
                if example.is_negated() != (atom in self.facts):
                    self.covered.add(Literal.Builder(atom).set_negated(example.is_negated()).build())
                else:
                    self.uncovered.add(Literal.Builder(atom).set_negated(example.is_negated()).build())
            return Hypothesis(self)

        def clear(self):
            self.covered.clear()
            self.literals.clear()
            self.model.clear()
            return self

        def parse(self, answer):
            if answer is None:
                raise ValueError(f"Illegal 'answer' argument in Hypothesis.Builder.parse(answer): {answer}")
            for atom in answer:
                self.add_atom(Parser.parse_token(atom))
            return self

        def remove_atom(self, atom):
            if atom is None:
                raise ValueError(f"Illegal 'builder' argument in Hypothesis.Builder.remove_atom(atom): {atom}")
            if atom.get_identifier() == "use_clause_literal" and 2 == atom.get_arity():
                self.literals.remove(atom)
            else:
                if self.grounding.get_config().is_full() and self.grounding.has_dispaly() and self.grounding.look_up(atom):
                    self.model.remove(atom)
                self.facts.remove(atom)
            return self

        def remove_atoms(self, atoms):
            if atoms is None:
                raise ValueError(f"Illegal 'builder' argument in Hypothesis.Builder.remove_atoms(atoms): {atoms}")
            for atom in atoms:
                self.remove_atom(atom)
            return self

    covered = None
    grounding = None
    hypotheses = None
    literals = None
    model = None
    uncovered = None

    def __init__(self, builder):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Hypothesis(hypothesis): {builder}")
        self.covered = list(builder.covered)
        self.grounding = builder.grounding
        self.literals = list(builder.literals)
        self.model = list(builder.model)
        if builder.uncovered is not None:
            self.uncovered = list(builder.uncovered)

    def __eq__(self, other):
        if not isinstance(other, Hypothesis):
            return NotImplemented
        return (self.hypotheses == other.hypotheses and
                self.covered == other.covered and
                (self.grounding == other.grounding or
                 self.grounding is not None and self.grounding == other.grounding) and
                self.literals == other.literals and
                self.model == other.model and
                self.uncovered == other.uncovered)

    def get_background(self):
        return self.grounding.get_background()

    def get_config(self):
        return self.grounding.get_config()

    def get_covered(self):
        return self.covered

    def get_delta(self):
        return self.grounding.get_delta()

    def get_display(self):
        return self.grounding.get_display()

    def get_domains(self):
        return self.grounding.get_domains()

    def get_examples(self):
        return self.grounding.get_examples()

    def get_generalisation(self):
        return self.grounding.get_generalisation()

    def get_grounding(self):
        return self.grounding

    def get_hypotheses(self):
        if self.hypotheses is None:
            set_clauses = set()
            generalisation = self.grounding.get_generalisation()
            builders = {}
            types = {}

            for atom in self.literals:
                clause_id = int(atom.get_term(0).get_value())
                literal_id = int(atom.get_term(1).get_value())
                if literal_id == 0 and 0 <= clause_id < len(generalisation):
                    builders[clause_id] = Clause.Builder().set_head(generalisation[clause_id].get_head())
                    types[clause_id] = set()

            for atom in self.literals:
                clause_id = int(atom.get_term(0).get_value())
                literal_id = int(atom.get_term(1).get_value())
                if literal_id > 0 and 0 <= clause_id < len(generalisation):
                    literal = generalisation[clause_id].get_body(literal_id)
                    builders[clause_id].add_literal(literal)
                    literals_set = types[clause_id]
                    for variable in literal.get_variables():
                        literals_set.add(Literal.Builder(
                            Atom.Builder(variable.get_type().get_identifier()).add_term(variable).build()
                        ).build())

            for c in builders.keys():
                builder = builders[c]
                for literal in types[c]:
                    builder.add_literal(literal)
                set_clauses.add(builder.build())

            self.hypotheses = list(set_clauses)
        return self.hypotheses

    def get_kernel(self):
        return self.grounding.get_kernel()

    def get_modeBs(self):
        return self.grounding.get_modeBs()

    def get_modeHs(self):
        return self.grounding.get_modeHs()

    def get_model(self):
        return self.model

    def get_problem(self):
        return self.grounding.get_problem()

    def get_uncovered(self):
        return self.uncovered

    def has_background(self):
        return self.grounding.has_background()

    def has_covered(self):
        return len(self.covered) > 0

    def has_delta(self):
        return self.grounding.has_delta()

    def has_displays(self):
        return self.grounding.has_displays()

    def has_domains(self):
        return len(self.grounding.get_domains()) > 0

    def has_examples(self):
        return self.grounding.has_examples()

    def has_generalisation(self):
        return self.grounding.has_generalisation()

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + hash(tuple(self.hypotheses))
        result = prime * result + hash(tuple(self.covered))
        result = prime * result + 0 if self.grounding is None else hash(self.grounding)
        result = prime * result + hash(tuple(self.literals))
        result = prime * result + hash(tuple(self.model))
        if self.uncovered is not None:
            result = prime * result + hash(tuple(self.uncovered))
        else:
            result = prime * result
        return result

    def has_hypotheses(self):
        return len(self.hypotheses) > 0

    def has_kernel(self):
        return self.grounding.has_kernel()

    def has_model(self):
        return len(self.model) > 0

    def has_modes(self):
        return self.grounding.has_modes()

    def has_uncovered(self):
        if self.uncovered is None:
            return False
        return len(self.uncovered) > 0

    def __iter__(self):
        return self.literals[:]

    def __str__(self):
        return (f"Hypothesis [\n"
                f"  hypotheses={self.hypotheses},\n"
                f"  covered={self.covered},\n"
                f"  grounding={self.grounding},\n"
                f"  literals={self.literals},\n"
                f"  model={self.model},\n"
                f"  uncovered={self.uncovered}\n"
                f"]")

