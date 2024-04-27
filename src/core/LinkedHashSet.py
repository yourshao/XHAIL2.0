class LinkedHashSet:
    def __init__(self):
        self.data = {}

    def add(self, item):
        if isinstance(item, set):
            item = frozenset(item)
        self.data[item] = None

    def remove(self, item):
        del self.data[item]

    def contains(self, item):
        return item in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def clear(self):
        self.data.clear()

    def __hash__(self):
        result = 1
        prime = 31
        for key in self.data:
            result = prime * result + hash(key)
        return result

