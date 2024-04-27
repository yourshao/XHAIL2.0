import logging as Logger
from typing import Tuple, Collection, Set

from src.core.entities.Values import Values
from src.core.parser.Parser import ParserErrorException
from src.core.parser.Tokeniser import Tokeniser


class Acquirer:
    FOUND = "FOUND"
    OPTIMIZATION = "Optimization:"
    OPTIMUM = "OPTIMUM"
    SATISFIABLE = "SATISFIABLE"
    UNKNOWN = "UNKNOWN"
    UNSATISFIABLE = "UNSATISFIABLE"

    def __init__(self, tokenisers):
        if tokenisers is None:
            raise ValueError("Illegal 'tokeniser' argument in Acquirer(Tokeniser): None")
        self.tokeniser = tokenisers
        self.token = self.tokeniser.next()
        # answers类型不对，现在可以重复
        self.answers = []
        self.atoms: Set[str] = set()
        self.values = Values()

    @staticmethod
    def from_stream(stream):
        if stream is None:
            raise ValueError("Illegal 'stream' argument in Acquirer.from(InputStream): None")
        return Acquirer(Tokeniser.from_stream(stream))

    def is_number(self, token):
        token = token.strip()
        if token is not None and token != "":
            result = True
            for char in token:
                result = char.isdigit()
            return result
        return False

    def parse(self) -> Tuple[Values, Collection[Collection[str]]]:
        try:
            if self.token == self.UNKNOWN:
                self.parse_unknown()
            elif self.token == self.UNSATISFIABLE:
                self.parse_unsatisfiable()
            else:
                self.parse_answer()
            self.parse_eof()
        except ParserErrorException as e:
            Logger.error(e)
        # return self.values, self.answers
        return {self.values:self.answers}


    def parse_answer(self):
        if self.token is None:
            raise ParserErrorException("expected ATOM but EOF found")
        else:
            self.atoms = set()
            while self.token is not None and self.token not in (self.FOUND, self.OPTIMIZATION, self.OPTIMUM, self.SATISFIABLE, self.UNKNOWN, self.UNSATISFIABLE):
                self.atoms.add(self.token)
                self.token = self.tokeniser.next()
            if self.token == self.SATISFIABLE:
                self.parse_satisfiable()
                self.answers.append(list(self.atoms))
            else:
                self.parse_optimization()
                self.parse_values()

    def parse_eof(self):
        # 这里可能是因为 我输入文件采取了 一行一行的方式
        if self.token == "Models" or self.token == "Optimization" or self.token == "Optimum" or self.token == "Satisfiable" or self.token == "Calls" or self.token == "Time" or self.token == "CPU":
            self.token = None
        if self.token is not None:
            raise ParserErrorException(f"expected EOF but '{self.token}' found")

    def parse_found(self):
        if self.token is None:
            raise ParserErrorException(f"expected '{self.FOUND}' but 'EOF' found")
        if self.token != self.FOUND:
            raise ParserErrorException(f"expected '{self.FOUND}' but '{self.token}' found")
        self.token = self.tokeniser.next()

    def parse_nested(self):
        if self.token is None:
            raise ParserErrorException("expected ATOM but EOF found")
        self.atoms = set()
        while self.token is not None and self.token not in (self.FOUND, self.OPTIMIZATION, self.OPTIMUM, self.SATISFIABLE, self.UNKNOWN, self.UNSATISFIABLE):
            self.atoms.add(self.token)
            self.token = self.tokeniser.next()
        self.parse_optimization()
        self.parse_values()

    def parse_optimization(self):
        if self.token is None:
            raise ParserErrorException(f"expected '{self.OPTIMIZATION}' but 'EOF' found")
        if self.token != self.OPTIMIZATION:
            raise ParserErrorException(f"expected '{self.OPTIMIZATION}' but '{self.token}' found")
        self.token = self.tokeniser.next()

    def parse_optimum(self):
        if self.token is None:
            raise ParserErrorException(f"expected '{self.OPTIMUM}' but 'EOF' found")
        if self.token != self.OPTIMUM:
            raise ParserErrorException(f"expected '{self.OPTIMUM}' but '{self.token}' found")
        self.token = self.tokeniser.next()

    def parse_satisfiable(self):
        if self.token is None:
            raise ParserErrorException(f"expected '{self.SATISFIABLE}' but 'EOF' found")
        if self.token != self.SATISFIABLE:
            raise ParserErrorException(f"expected '{self.SATISFIABLE}' but '{self.token}' found")
        self.token = self.tokeniser.next()

    def parse_unknown(self):
        if self.token is None:
            raise ParserErrorException(f"expected '{self.UNKNOWN}' but 'EOF' found")
        if self.token != self.UNKNOWN:
            raise ParserErrorException(f"expected '{self.UNKNOWN}' but '{self.token}' found")
        self.token = self.tokeniser.next()

    def parse_unsatisfiable(self):
        if self.token is None:
            raise ParserErrorException(f"expected '{self.UNSATISFIABLE}' but 'EOF' found")
        if self.token != self.UNSATISFIABLE:
            raise ParserErrorException(f"expected '{self.UNSATISFIABLE}' but '{self.token}' found")
        self.token = self.tokeniser.next()

    def parse_values(self):
        if self.token is None:
            raise ParserErrorException("expected NUMBER but EOF found")
        elif not self.is_number(self.token):
            raise ParserErrorException(f"expected NUMBER but '{self.token}' found")
        else:
            values = ""

            while self.token is not None and self.is_number(self.token):
                if values != "":
                    values += " "
                values += self.token
                self.token = self.tokeniser.next()

            found = Values(values)
            order = found.compare_to(self.values)
            if order < 0:
                self.answers.clear()
                self.values = found

            if order <= 0:
                # 应该是add，但是改成了【】 就是为了可以添加set 不然不让加入
                self.answers.append(self.atoms)

            if self.token == "OPTIMUM":
                self.parse_optimum()
                self.parse_found()
            else:
                self.parse_nested()

