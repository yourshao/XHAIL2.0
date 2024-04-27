class StringIterator:
    def __init__(self, source):
        self.source = source
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.has_next():
            result = self.source[self.index]
            self.index += 1
        else:
            result = None
        return result


    def has_next(self):
        return self.index < len(self.source)


    def next(self):
        return self.__next__()