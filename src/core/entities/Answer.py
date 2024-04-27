# Author: Zhenqun Shao
# Date: 2024-3-30
# Project: XHAIL UP DATE
# Description: Pre version author @stefano
from src.core.Buildable import Buildable
from src.core.terms.Clause import Clause



class Answer:
    def __init__(self, grounding=None, hypothesis=None):
        self.grounding = grounding
        self.hypothesis = hypothesis

    class Builder(Buildable):
        def __init__(self, grounding):
            if grounding is None:
                raise ValueError(f"Illegal 'builder' argument in Answer.Builder(grounding): {grounding}")
            self.answer = Answer()
            self.answer.grounding = grounding

        def set_hypothesis(self, hypothesis):
            if hypothesis is None:
                raise ValueError(f"Illegal 'builder' argument in Answer.Builder(hypothesis): {hypothesis}")
            self.answer.hypothesis = hypothesis
            return self

        def build(self):
            return self.answer

    def __eq__(self, other):
        if not isinstance(other, Answer):
            return False
        if other is None:
            return False
        return self.grounding == other.grounding and self.hypothesis == other.hypothesis

    def get_covered(self):
        if self.hypothesis is None:
            return self.grounding.get_covered()
        return self.hypothesis.get_covered()

    def get_delta(self):
        return self.grounding.get_delta()

    def get_domains(self):
        return self.grounding.get_domains()

    def get_grounding(self):
        return self.grounding

    def get_hypotheses(self):
        if self.hypothesis is None:
            return Clause()
        return self.hypothesis.get_hypotheses()

    def get_hypothesis(self):
        return self.hypothesis

    def get_kernel(self):
        return self.grounding.get_kernel()

    def get_model(self):
        if self.hypothesis is None:
            return self.grounding.get_model()
        return self.hypothesis.get_model()

    def get_program(self):
        return self.grounding.get_program()

    def get_uncovered(self):
        if self.hypothesis is None:
            return self.grounding.get_uncovered()
        return self.hypothesis.get_uncovered()

    def get_background(self):
        return self.grounding.get_background()

    def has_covered(self):
        if self.hypothesis is None:
            return self.grounding.has_covered()
        return self.hypothesis.has_covered()

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
        result = prime * result + hash(self.grounding)
        result = prime * result + hash(self.hypothesis)
        return result

    def has_hypotheses(self):
        return self.hypothesis.has_hypotheses()

    def has_kernel(self):
        return self.grounding.has_kernel()

    def has_model(self):
        if self.hypothesis is None:
            return False
        return self.hypothesis.has_model()

    def is_meaningful(self):
        return self.hypothesis is not None and len(self.hypothesis.get_hypotheses()) > 0

    def has_uncovered(self):
        if self.hypothesis is None:
            return self.grounding.has_uncovered()
        return self.hypothesis.has_uncovered()

    def __str__(self):
        return f"Answer [\n  grounding={self.grounding},\n hypothesis={self.hypothesis}\n]"






















