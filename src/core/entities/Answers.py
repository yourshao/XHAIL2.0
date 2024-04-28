from src.core.Buildable import Buildable
from src.core.entities.Answer import Answer
from src.core.Config import Config
from src.core.entities.Grounding import Grounding
from src.core.entities.Hypothesis import Hypothesis
# from src.core.entities.Problem import Problem
# from src.core.entities.Grounding import Grounding

import time


class Answers:
    def __init__(self, builder: 'Answers.Builder'):
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Answers(builder): {builder}")
        self.answers = list(builder.answers)
        self.config = builder.config
        self.count = builder.count
        self.values = builder.values

    NORMALIZER = 100_000_000.0
    # answers = []
    # config = []
    # count = 0
    # values = []
    abduction = 0
    deduction = 0
    first = -1
    induction = 0
    loading = -1
    start = -1

    class Builder(Buildable):
        answers = set()
        config = None
        count = 0
        values = -1

        def __init__(self, config):
            if config is None:
                raise ValueError(f"Illegal 'builder' argument in Answers.Builder(config): {config}")
            self.answers = set()
            self.config = config
            self.count = 0
            self.values = -1

        def build(self):
            return Answers(self)

        def clear(self):
            Answers.first = -1
            self.answers.clear()
            self.count = 0
            self.values = -1
            return self

        def is_meaningful(self):
            for answer in self.answers:
                if answer.is_meaningful():
                    return True
            return False

        def put(self, values, answer):
            if values is None or answer is None:
                raise ValueError(f"Illegal 'values' or 'answer' argument: {values}, {answer}")
            else:
                if Answers.first < 0:
                    Answers.first = time.time_ns()
                if self.values is None:
                    order = -1
                else:
                    order = values.compare_to(self.values)
                if order < 0:
                    self.answers.clear()
                    self.values = values
                if order <= 0:
                    self.answers.add(answer)
                self.count += 1
                return self

        def remove(self, values, answer):
            if values is None or answer is None:
                raise ValueError(f"Illegal 'values' or 'answer' argument: {values}, {answer}")
            if self.values is not None and self.values == values:
                if answer in self.answers:
                    self.answers.remove(answer)
                    self.count -= 1
            return self

        def size(self):
            return len(self.answers)

    def size(self):
        return len(self.answers)


    @staticmethod
    def get_abduction():
        return Answers.abduction/Answers.NORMALIZER

    @staticmethod
    def get_deduction():
        return Answers.deduction/Answers.NORMALIZER

    @staticmethod
    def get_first():
        if Answers.start < 0 or Answers.first < 0:
            return 0
        return (Answers.first - Answers.start) / Answers.NORMALIZER

    @staticmethod
    def get_induction():
        return Answers.induction/Answers.NORMALIZER

    @staticmethod
    def get_loading():
        if Answers.loading < 0 or Answers.start < 0:
            return 0
        return (Answers.loading - Answers.start) / Answers.NORMALIZER

    @staticmethod
    def get_now():
        if Answers.start < 0:
            return 0
        return (time.time_ns() - Answers.start) / Answers.NORMALIZER

    @staticmethod
    def loaded():
        if Answers.loading < 0:
            Answers.loading = time.time_ns()

    @staticmethod
    def started():
        if Answers.start < 0:
            Answers.start = time.time_ns()

    @staticmethod
    def time_abduction(iteration, dialer):
        if iteration < 0:
            raise ValueError(f"Illegal 'time_abduction' argument in Answers.time_abduction(iter): {iteration}")
        if dialer is None:
            raise ValueError(f"Illegal 'time_abduction' argument in Answers.time_abduction(dialer): {dialer}")
        start_time = time.time_ns()
        result = dialer.execute(iteration)
        Answers.abduction += time.time_ns() - start_time
        return result

    @staticmethod
    def time_deduction(grounding_or_problem, output):
        if grounding_or_problem is None:
            raise ValueError(f"Illegal 'timeDeduction' argument in Answers.timeDeduction(grounding_or_problem): {grounding_or_problem}")
        if output is None:
            raise ValueError(f"Illegal 'timeDeduction' argument in Answers.timeDeduction(output): {output}")
        start_time = time.time_ns()
        if grounding_or_problem.is_problem():
            result = Grounding.Builder(grounding_or_problem).parse(output).build()
            result.get_generalisation()
        elif not grounding_or_problem.is_problem():
            result = Hypothesis.Builder(grounding_or_problem).parse(output).build()
            result.get_hypotheses()
        else:
            raise ValueError(f"Illegal 'timeDeduction' argument in Answers.timeDeduction(grounding_or_problem): {grounding_or_problem}")
        Answers.deduction += time.time_ns() - start_time
        return result

    @staticmethod
    def time_induction(iteration, dialler):
        if iteration < 0:
            raise ValueError(f"Illegal 'time_induction' argument in Answers.time_induction(iter): {iteration}")
        if dialler is None:
            raise ValueError(f"Illegal 'time_induction' argument in Answers.time_induction(dialer): {dialler}")
        start_time = time.time_ns()
        result = dialler.execute(iteration)
        Answers.induction += time.time_ns() - start_time
        return result

    def __eq__(self, other):
        if self is other:
            return True
        if other is None or not isinstance(other, self.__class__):
            return False
        if list(self.answers) == list(other.answers):
            return True
        if self.values is None:
            if other.values is not None:
                return False
        elif self.values != other.values:
            return False
        return True

    def get_answer(self, index):
        if index < 0 or index >= len(self.answers):
            raise ValueError(f"Illegal 'get_answer' argument in Answers.get_answer(index): {index}")
        return self.answers[index]

    def get_answers(self):
        return self.answers

    def get_config(self):
        return self.config

    def get_values(self):
        return self.values

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + hash(tuple(self.answers))
        if self.values is not None:
            result = prime * result + hash(tuple(self.values))

        return result

    def is_empty(self):
        return len(self.answers) == 0

    def __iter__(self):
        return iter(self.answers[:])

    def __len__(self):
        return len(self.answers)
