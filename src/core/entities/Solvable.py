from abc import ABCMeta, abstractmethod

class Solvable(metaclass=ABCMeta):

    @abstractmethod
    def save(self, iters, stream):
        pass

    @abstractmethod
    def is_problem(self):
        pass