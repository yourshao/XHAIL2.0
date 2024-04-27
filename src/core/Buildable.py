from abc import ABCMeta, abstractmethod



class Buildable(metaclass=ABCMeta):
    @abstractmethod
    def build(self):
        pass


