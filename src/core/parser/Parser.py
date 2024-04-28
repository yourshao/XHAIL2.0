from src.core.Logger_copy import Logger
from src.core.terms.Atom import Atom
from src.core.statements.Display import Display
from src.core.statements.Example import Example
from src.core.terms.Number import Number
from src.core.statements.ModeB import ModeB
from src.core.statements.ModeH import ModeH
from src.core.terms.Type import Type
from src.core.terms.Placemarker import Placemarker
from src.core.terms.Quotation import Quotation
from src.core.terms.Scheme import Scheme
from src.core.terms.Variable import Variable
from src.core.parser.StringIterator import StringIterator


class ParserErrorException(Exception):
    serialVersionUID = 13145208618860670997

    def __init__(self, message):
        super().__init__(message)


class Parser:
    class StringIterator:
        pos = 1
        source = None

        def __init__(self, source):
            self.source = source

        def has_next(self):
            return False if self.source is None else len(self.source) > 1 + self.pos

        def next(self):
            if self.has_next():
                self.pos += 1
                return self.source[self.pos]
            else:
                return None

        def push_back(self):
            if self.pos > -1:
                self.pos -= 1

    @staticmethod
    def parse_answer_1(source):
        if source is None:
            raise ValueError("Illegal 'source' argument in Parser.parse_answer_1(source): None")
        parser = source
        try:
            result = parser.parse_answer_0()
            parser.parseEOF()
            return result
        except ParserErrorException as e:
            Logger.error(str(e))
            return None

    @staticmethod
    def parse_display_1(source):
        if source is None:
            raise ValueError("Illegal 'source' argument in Parser.parse_display_1(source): None")
        parser = Parser(source)
        try:
            result = parser.parse_display_0()
            parser.parse_EOF()
            return result
        except ParserErrorException as e:
            Logger.error(str(e))
            return None

    @staticmethod
    def parse_example_1(source):
        if source is None:
            raise ValueError("Illegal 'source' argument in Parser.parse_example_1(source): None")
        parser = Parser(source)
        try:
            result = parser.parse_example_0()
            parser.parse_EOF()
            return result
        except ParserErrorException as e:
            Logger.error(str(e))
            return None

    @staticmethod
    def parse_token(token):
        if token is None:
            raise ValueError("Illegal 'token' argument in Parser.parse_token(token): None")
        parser = Parser(token)
        try:
            result = parser.parse_ground_atom()
            parser.parse_EOF()
            return result
        except ParserErrorException as e:
            Logger.error(str(e))
            return None

    @staticmethod
    def parse_modeB_1(source):
        if source is None:
            raise ValueError("Illegal 'source' argument in Parser.parse_modeB_1(source): None")
        try:
            parser = Parser(source)
            result = parser.parse_modeB_0()
            parser.parse_EOF()
            return result
        except ParserErrorException as e:
            Logger.error(str(e))
            return None

    @staticmethod
    def parse_modeH_1(source):
        if source is None:
            raise ValueError("Illegal 'source' argument in Parser.parse_modeH_1(source): None")
        try:
            parser = Parser(source)
            result = parser.parse_modeH_0()
            parser.parse_EOF()
            return result
        except ParserErrorException as e:
            Logger.error(str(e))
            return None

    current = None
    iterator = None
    source = None

    def __init__(self, source):
        if source is None:
            raise ValueError(f"Illegal 'source' argument in Parser(source): {source}")
        self.source = source
        self.iterator = StringIterator(source)
        self.current = self.iterator.next()

    def skip(self):
        while self.current is not None and self.current <= ' ':
            self.current = self.iterator.next()

    def get_source(self):
        return self.source

    def parse_answer_0(self):
        # raise ParserErrorException()
        self.skip()
        result = set()
        while self.current and self.current.islower():
            result.add(self.parse_ground_atom())
            self.skip()
        return result

    def parse_at(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected '@' but EOF found in \' {self.source} \'")
        if self.current != '@':
            raise ParserErrorException(f"expected '@' but '{self.current}' found in \' {self.source} \'")
        if self.iterator.has_next():
            self.current = self.iterator.next()

    def parse_atom(self):
        result = Atom.Builder(self.parse_identifier())
        self.skip()
        if self.current is not None and self.current == '(':
            self.parse_left_paren()
            result.add_term(self.parse_term())
            self.skip()
            while self.current is not None and self.current == ',':
                self.parse_comma()
                result.add_term(self.parse_term())
                self.skip()
            self.parse_right_paren()
        return result.build()

    def parse_colon(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected ':' but EOF found in \' {self.source} \'")
        if self.current != ':':
            raise ParserErrorException(f"expected ':' but '{self.current}' found in \' {self.source} \'")
        self.current = self.iterator.next()

    def parse_comma(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected ',' but EOF found in \' {self.source} \'")
        if self.current != ',':
            raise ParserErrorException(f"expected ',' but '{self.current}' found in \' {self.source} \'")
        self.current = self.iterator.next()

    def parse_dash(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected '-' but EOF found in \' {self.source} \'")
        if self.current != '-':
            raise ParserErrorException(f"expected '-' but '{self.current}' found in \' {self.source} \'")
        self.current = self.iterator.next()

    def parse_display_0(self):
        identifier = self.parse_identifier()
        self.parse_slash()
        if self.current is None:
            raise ParserErrorException(f"expected '0..9' but EOF found in '{self.source}'")
        if not self.current.isdigit():
            raise ParserErrorException(f"expected '0..9' but '{self.current}' found in '{self.source}'")
        number = self.parse_number()
        return Display.Builder(identifier).set_arity(number.get_value()).build()

    def parse_EOF(self):
        self.skip()
        if self.current is not None:
            raise ParserErrorException(f"expected EOF but '{self.current}' found in '{self.source}'")

    def parse_equal(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected '=' but EOF found in '{self.source}'")
        if self.current != '=':
            raise ParserErrorException(f"expected '=' but '{self.current}' found in '{self.source}'")
        self.current = self.iterator.next()

    def parse_example_0(self):
        atom = self.parse_ground_atom()
        negated = "not" == atom.get_identifier()
        if negated:
            atom = self.parse_ground_atom()
        result = Example.Builder(atom).set_negated(negated)
        if self.current is not None and self.current == '=':
            self.parse_equal()
            result.set_weight(self.parse_number().get_value())
        if self.current is not None and self.current == '@':
            self.parse_at()
            result.set_priority(self.parse_number().get_value())
        return result.build()

    def parse_ground_atom(self):
        result = Atom.Builder(self.parse_identifier())
        self.skip()
        if self.current is not None and self.current == '(':
            self.parse_left_paren()
            result.add_term(self.parse_ground_term())
            self.skip()
            while self.current is not None and self.current == ',':
                self.parse_comma()
                result.add_term(self.parse_ground_term())
                self.skip()
            self.parse_right_paren()
        return result.build()

    def parse_ground_term(self):
        if self.current is None:
            raise ParserErrorException(f"expected '0..9' but EOF found in '{self.source}'")
        if self.current.islower():
            return self.parse_atom()
        if self.current.isdigit() or self.current == '-':
            return self.parse_number()
        if self.current == '"':
            return self.parse_quotation()
        raise ParserErrorException(f"expected 'TERM' but '{self.current}' found in '{self.source}'")

    def parse_identifier(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected 'a..z' but EOF found in '{self.source}'")
        elif not self.current.islower():
            raise ParserErrorException(f"expected 'a..z' but '{self.current}' found in '{self.source}'")
        else:
            result = ""
            while self.current is not None and (self.current.isalnum() or self.current == '_'):
                result += self.current
                self.current = self.iterator.next()
            return result

    def parse_left_paren(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected '(' but EOF found in '{self.source}'")
        if self.current != '(':
            raise ParserErrorException(f"expected '(' but '{self.current}' found in '{self.source}'")
        self.current = self.iterator.next()

    def parse_modeB_0(self):
        scheme = self.parse_scheme()
        negated = ("not" == scheme.get_identifier())

        if negated:
            scheme = self.parse_scheme()

        result = ModeB.Builder(scheme).set_negated(negated)
        if self.current is not None and self.current == ':':
            self.parse_colon()
            result.set_upper(self.parse_number().get_value())
        if self.current is not None and self.current == '=':
            self.parse_equal()
            result.set_weight(self.parse_number().get_value())
        if self.current is not None and self.current == '@':
            self.parse_at()
            result.set_priority(self.parse_number().get_value())
        return result.build()

    def parse_modeH_0(self):
        result = ModeH.Builder(self.parse_scheme())
        if self.current is not None and self.current == ":":
            self.parse_colon()
            value = self.parse_number().get_value()
            if self.current is not None and self.current == '-':
                result.set_lower(value)
                self.parse_dash()
                result.set_upper(self.parse_number().get_value())
            else:
                result.set_upper(value)
        if self.current is not None and self.current == '=':
            self.parse_equal()
            result.set_weight(self.parse_number().get_value())
        if self.current is not None and self.current == '@':
            self.parse_at()
            result.set_priority(self.parse_number().get_value())
        return result.build()

    def parse_number(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected '0..9' or '-' but EOF found in '{self.source}'")
        else:
            negative = (self.current == '-')
            if negative:
                self.current = self.iterator.next()
                self.skip()
            if self.current is None:
                raise ParserErrorException(f"expected '0..9' but EOF found in '{self.source}'")
            elif not self.current.isdigit():
                raise ParserErrorException(f"expected '0..9' but '{self.current}' found in '{self.source}'")
            else:
                # 不同
                result = int(self.current)
                self.current = self.iterator.next()
                while self.current is not None and self.current.isdigit():
                    result = result * 10 + int(self.current)
                    self.current = self.iterator.next()
                result = -result if negative else result
                return Number.Builder(result).build()

        # if self.iterator.has_next():
        #     self.current = self.iterator.next()
        # while self.current is not None and self.current.isdigit():
        #     result = result * 10 + int(self.current) - 48
        #     self.current = self.iterator.next()
        #     result = -result if negative else result
        # return Number.Builder(result).build()

    def parse_placemarker(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected '?' but EOF found in '{self.source}'")
        else:
            if self.current == '+':
                type = Type.INPUT
                self.current = self.iterator.next()
            elif self.current == '-':
                type = Type.OUTPUT
                self.current = self.iterator.next()
            else:
                if self.current != '$':
                    raise ParserErrorException(
                        f"expected '?', '+', '-' or '$' but '{self.current}' found in '{self.source}'")
                type = Type.CONSTANT
                self.current = self.iterator.next()
        return Placemarker.Builder(self.parse_identifier()).set_type(type).build()

    def parse_quotation(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected '\"' but EOF found in '{self.source}'")
        if self.current != '"':
            raise ParserErrorException(f"expected '\"' but '{self.current}' found in '{self.source}'")
        result = "" + self.current
        self.current = self.iterator.next()
        while self.current is not None and self.current != '"':
            result += self.current
            self.current = self.iterator.next()
        if self.current is None:
            raise ParserErrorException(f"expected '\"' but EOF found in '{self.source}'")
        result += self.current
        self.current = self.iterator.next()
        return Quotation.Builder(result).build()

    def parse_right_paren(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected ')' but EOF found in '{self.source}'")
        elif self.current != ")":
            raise ParserErrorException(f"expected ')' but '{self.current}' found in '{self.source}'")
        else:
            self.current = self.iterator.next()

    def parse_scheme(self):
        result = Scheme.Builder(self.parse_identifier())
        self.skip()
        if self.current is not None and self.current == '(':
            self.parse_left_paren()
            result.add_term(self.parse_scheme_term())
            self.skip()
            while self.current is not None and self.current == ',':
                self.parse_comma()
                result.add_term(self.parse_scheme_term())
                self.skip()

            self.parse_right_paren()

        return result.build()
        #
        # def parse_scheme_term(self):
        #     self.skip()
        # if self.current is None:
        #     raise ParserErrorException(f"expected 'SCHEMETERM' but EOF found in '{self.source}'")
        # elif self.current.islower():
        #     return self.parse_scheme()
        # elif self.current is not '+' or self.current is not '-' or self.current is not '$':
        #
        #
        #
        #
        #
        #
        #     return self.parse_placemarker()
        # if self.current.isdigit() or self.current == '-':
        #     return self.parse_number()
        # if self.current == '"':
        #     return self.parse_quotation()
        # raise ParserErrorException(f"expected 'SCHEMETERM' but '{self.current}' found in '{self.source}'")
        #
        #
        #

    def parse_scheme_term(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected 'SCHEMETERM' but EOF found in '{self.source}'")
        elif self.current.islower():
            return self.parse_scheme()
        elif self.current != '+' and self.current != '-' and self.current != '$':
            if not self.current.isdigit() and self.current != '-':
                if self.current == '"':
                    return self.parse_quotation()
                else:
                    raise ParserErrorException(f"expected 'SCHEMETERM' but '{self.current}' found in '{self.source}'")
            else:
                return self.parse_number()
        else:
            return self.parse_placemarker()

    def parse_slash(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected '/' but EOF found in '{self.source}'")
        if self.current != '/':
            raise ParserErrorException(f"expected '/' but '{self.current}' found in '{self.source}'")
        self.current = self.iterator.next()

    def parse_term(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected '0..9' but EOF found in '{self.source}'")
        if self.current.islower():
            return self.parse_atom()
        if self.current.isupper() or self.current == '_':
            return self.parse_variable()
        if self.current.isdigit() or self.current == '-':
            self.parse_number()
        if self.current == '"':
            self.parse_quotation()
        raise ParserErrorException(f"expected 'TERM' but '{self.current}' found in '{self.source}'")

    def parse_variable(self):
        self.skip()
        if self.current is None:
            raise ParserErrorException(f"expected 'A..Z' or '_' but EOF found in '{self.source}'")
        if not self.current.isupper() and self.current != '_':
            raise ParserErrorException(f"expected 'A..Z' or '_' but '{self.current}' found in '{self.source}'")
        result = ""
        while self.current is not None and (self.current.isalnum() or self.current == '_'):
            result += self.current
            self.current = self.iterator.next()
        return Variable.Builder(result).build()
