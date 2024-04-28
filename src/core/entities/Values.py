import sys
import re


class Values:
    def __init__(self, *args):
        if len(args) == 0:
            self.source = "2147483647"
            self.values = [sys.maxsize]
        elif isinstance(args[0], tuple) or isinstance(args[0], str):
                values = args[0]
                # self.source = str(values)
                # self.values = []
                # self.values.append(int(item) for item in values)
                if values is not None and len(values) > 0:
                    try:
                        self.source = values
                        converted = re.split(r'\s+', values)
                        self.values = [int(val) for val in converted]
                    except Exception as e:
                        raise ValueError(f"Illegal 'values' argument in Values(String): {e}")
                else:
                    raise ValueError(f"Illegal 'values' argument in Values(String): {values}")
        else:
            for values in args:
                for value in values:
                    self.source = value.source
                    self.values = value.values[:]

    def __lt__(self, other):
        if not isinstance(other, Values):
            return False
        if other is None:
            return False
        for i in range(min(len(self.values), len(other.values))):
            if self.values[i] < other.values[i]:
                return True
            elif self.values[i] > other.values[i]:
                return False
        return len(self.values) < len(other.values)

    def __eq__(self, other):
        if not isinstance(other, Values):
            return False
        return self.source == other.source and self.values == other.values

    def __hash__(self):
        return hash((self.source, tuple(self.values)))

    def get_value(self, index):
        if index < 0 or index >= len(self.values):
            raise IndexError(f"Illegal 'index' argument in Values.getValue(): {index}")
        return self.values[index]

    def get_values(self):
        return self.values[:]

    def matches(self, values):
        values = values.strip()
        if not values:
            raise ValueError(f"Illegal 'values' argument in Values.matches(String): {values}")
        return self.source == values



    def size(self):
        return len(self.values)

    def __str__(self):
        return self.source

    def compare_to(self, other):
        for i in range(min(len(self.values), len(other.values))):
            if self.values[i] < other.values[i]:
                return -1
            elif self.values[i] > other.values[i]:
                return 1

        return 0
