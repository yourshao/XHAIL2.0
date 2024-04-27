from src.core.terms.Atom import Atom
from src.core.terms.Number import Number
# from src.core.terms.Placemarker import Placemarker
from src.core.terms.Quotation import Quotation
from src.core.terms.Scheme import Scheme
from src.core.terms.Variable import Variable
from src.core.terms.Type import Type

from abc import ABCMeta, abstractmethod


CONSTANT_STRING = "internal_const_par"
INPUT_STRING = "internal_input_par"
OUTPUT_STRING = "internal_output_par"


class SchemeTerm(metaclass=ABCMeta):

    @staticmethod
    def generate_and_output_3(scheme, substitutes, table):
        # from src.core.terms.Placemarker import Placemarker
        if scheme is None:
            raise ValueError("Illegal 'scheme' argument in generate_and_output: None")
        if substitutes is None:
            raise ValueError("Illegal 'substitutes' argument in generate_and_output: None")
        if table is None:
            raise ValueError("Illegal 'table' argument in generate_and_output: None")

        builders = {Atom.Builder(scheme.get_identifier()): set()}
        for i in range(scheme.get_arity()):
            schemeterm = scheme.get_term(i)
            temporary = {}

            if isinstance(schemeterm, Number):
                for builder, value in builders.items():
                    new_value = set(value)
                    key = builder.add_term(schemeterm)
                    temporary[key] = new_value
            elif isinstance(schemeterm, Quotation):
                for builder, value in builders.items():
                    new_value = set(value)
                    key = builder.add_term(schemeterm)
                    temporary[key] = new_value
            elif schemeterm.is_placemarker():
                if schemeterm.get_type() == Type.INPUT:
                    for builder, value in builders.items():
                        for substitute in substitutes:
                            new_value = set(value)
                            key = builder.clone().add_term(substitute)
                            temporary[key] = new_value
                else:
                    is_output = schemeterm.get_type() == Type.OUTPUT
                    candidates = table.get(schemeterm)
                    for builder, value in builders.items():
                        for candidate in candidates:
                            utilise = candidate.get_term(0) if candidate.get_identifier() == schemeterm.get_identifier() and candidate.get_arity() == 1 else candidate
                            new_value = set(value)
                            if is_output:
                                new_value.add(utilise)
                            key = builder.clone().add_term(utilise)
                            temporary[key] = new_value
            else:  # if isinstance(schemeterm, Scheme)
                returned = SchemeTerm.generate_and_output_3(schemeterm, substitutes, table)
                for builder, value in builders.items():
                    for atom, returned_value in returned.items():
                        new_value = set(value)
                        new_value.update(returned_value)
                        key = builder.clone().add_term(atom)
                        temporary[key] = new_value

            builders = temporary

        result = {builder.build(): value for builder, value in builders.items()}
        return result

    @staticmethod
    def generate_and_output_4(scheme, substitutes, table, facts):
        if scheme is None:
            raise ValueError(f"Illegal 'scheme' argument in SchemeTerm.generate_output_4(scheme, substitutes, table, facts): {scheme}")
        if substitutes is None:
            raise ValueError(f"Illegal 'substitutes' argument in SchemeTerm.generate_output_4(scheme, substitutes, table, facts): {substitutes}")
        if table is None:
            raise ValueError(f"Illegal 'table' argument in SchemeTerm.generate_output_4(scheme, substitutes, table, facts): {table}")
        if facts is None:
            raise ValueError(f"Illegal 'facts' argument in SchemeTerm.generate_output_4(scheme, substitutes, table, facts): {facts}")
        generated = SchemeTerm.generate_and_output_3(scheme, substitutes, table)
        result = {}
        for atom in generated:
            if atom not in facts:
                result[atom] = generated[atom]
        return result

    @staticmethod
    def match_and_output(scheme, atoms_or_atom, substitutes):
        if not isinstance(atoms_or_atom, Atom):
            if scheme is None:
                raise ValueError("Illegal 'scheme' argument in match_and_output: None")
            if atoms_or_atom is None:
                raise ValueError("Illegal 'atoms' argument in match_and_output: None")
            if substitutes is None:
                raise ValueError("Illegal 'substitutes' argument in match_and_output: None")

            matches = set()
            outputs = set()
            for atom in atoms_or_atom:
                output = SchemeTerm.match_and_output(scheme, atom, substitutes)  # 假设此函数已定义
                if output is not None:
                    matches.add(atom)
                    outputs.update(output)

            return matches, outputs  # 返回一个包含两个集合的元组
        else:
            if scheme is None:
                raise ValueError("Illegal 'scheme' argument in match_and_output: None")
            if atoms_or_atom is None:
                raise ValueError("Illegal 'atom' argument in match_and_output: None")
            if substitutes is None:
                raise ValueError("Illegal 'substitutes' argument in match_and_output: None")

            if atoms_or_atom.get_identifier() != scheme.get_identifier() or atoms_or_atom.get_arity() != scheme.get_arity():
                return None

            result = set()
            for i in range(scheme.get_arity()):
                schemeterm = scheme.get_term(i)
                term = atoms_or_atom.get_term(i)

                if isinstance(schemeterm, Number):
                    if not isinstance(term, Number) or term.get_value() != schemeterm.get_value():
                        return None
                elif isinstance(schemeterm, Quotation):
                    if not isinstance(term, Quotation) or term.get_content() != schemeterm.get_content():
                        return None
                elif schemeterm.is_placemarker():
                    if schemeterm.get_type() == Type.INPUT:
                        if term not in substitutes:
                            return None
                    elif schemeterm.get_type() == Type.OUTPUT:
                        result.add(term)
                elif isinstance(schemeterm, Scheme):
                    if not isinstance(term, Atom):
                        return None
                    subresult = SchemeTerm.match_and_output(schemeterm, term, substitutes)
                    if subresult is None:
                        return None
                    result.update(subresult)
                else:
                    return None

            return result

    @staticmethod
    def is_matching(*args):
        if len(args) == 3:
            scheme, atom, substitutes = args
            if scheme is None:
                raise ValueError("Illegal 'scheme' argument in is_matching: None")
            if atom is None:
                raise ValueError("Illegal 'atom' argument in is_matching: None")
            if substitutes is None:
                raise ValueError("Illegal 'substitutes' argument in is_matching: None")

            if atom.get_identifier() != scheme.get_identifier() or atom.get_arity() != scheme.get_arity():
                return False

            for i in range(scheme.get_arity()):
                schemeterm = scheme.get_term(i)
                term = atom.get_term(i)

                if isinstance(schemeterm, Number):
                    if not isinstance(term, Number) or term.get_value() != schemeterm.get_value():
                        return False
                elif isinstance(schemeterm, Quotation):
                    if not isinstance(term, Quotation) or term.get_content() != schemeterm.get_content():
                        return False
                elif schemeterm.is_lacemarker():
                    if schemeterm.get_type() == Type.INPUT and term not in substitutes:
                        return False
                elif isinstance(schemeterm, Scheme):
                    if not isinstance(term, Atom) or not SchemeTerm.is_matching(schemeterm, term, substitutes):
                        return False
                else:
                    return False
            return True

        elif len(args) == 2:
            scheme, atom = args
            if scheme is None:
                raise ValueError("Illegal 'scheme' argument in is_matching: None")
            if atom is None:
                raise ValueError("Illegal 'atom' argument in is_matching: None")

            if atom.get_identifier() != scheme.get_identifier() or atom.get_arity() != scheme.get_arity():
                return False

            for i in range(scheme.get_arity()):
                schemeterm = scheme.get_term(i)
                term = atom.get_term(i)

                if isinstance(schemeterm, Number):
                    if not isinstance(term, Number) or term.get_value() != schemeterm.get_value():
                        return False
                elif isinstance(schemeterm, Quotation):
                    if not isinstance(term, Quotation) or term.get_content() != schemeterm.get_content():
                        return False
                elif schemeterm.is_placemarker():
                    # Assuming Placemarker logic is not needed based on the original Java snippet
                    continue
                elif isinstance(schemeterm, Scheme):
                    if not isinstance(term, Atom) or not SchemeTerm.is_matching(schemeterm, term):
                        return False
                else:
                    return False
            return True

    @staticmethod
    def look_up(modeHs, modeBs, facts):
        if modeHs is None:
            raise ValueError("Illegal 'modeHs' argument in lookup: None")
        if modeBs is None:
            raise ValueError("Illegal 'modeBs' argument in lookup: None")
        if facts is None:
            raise ValueError("Illegal 'facts' argument in lookup: None")

        result = {}
        for mode in modeHs:
            scheme = mode.get_scheme()
            if scheme not in result:
                result[scheme] = set()
            for placemarker in scheme.get_placemarkers_0():
                if placemarker not in result:
                    result[placemarker] = set()

        # 处理ModeB实例
        for mode in modeBs:
            scheme = mode.get_scheme()
            if scheme not in result:
                result[scheme] = set()
            for placemarker in scheme.get_placemarkers_0():
                if placemarker not in result:
                    result[placemarker] = set()


        for scheme, part in result.items():
            for fact in facts:
                if SchemeTerm.subsumes(scheme, fact, facts):  # 假设有一个subsumes函数
                    part.add(fact)

        return result


    @staticmethod
    def subsumes(scheme, term, facts):
        if scheme is None:
            raise ValueError("Illegal 'scheme' argument in subsumes: None")
        if term is None:
            raise ValueError("Illegal 'term' argument in subsumes: None")
        if facts is None:
            raise ValueError("Illegal 'facts' argument in subsumes: None")

        if isinstance(scheme, Scheme):
            if not isinstance(term, Atom):
                return False
            if term.get_identifier() != scheme.get_identifier() or term.get_arity() != scheme.get_arity():
                return False
            for i in range(scheme.get_arity()):
                if not SchemeTerm.subsumes(scheme.get_term(i), term.get_term(i), facts):
                    return False
            return True
        elif scheme.is_placemarker():
            if isinstance(term, Variable):
                return False  # Assuming AtomBuilder class is defined elsewhere

            if Atom.Builder(scheme.get_identifier()).add_term(term).build() in facts:
                return True
            if isinstance(term, Atom):
                return term.get_identifier() == scheme.get_identifier() and term.get_arity() == 1
            return False
        else:
            return False

    @staticmethod
    def find_substitutes(scheme, candidate):
        if scheme is None:
            raise ValueError("Illegal 'scheme' argument in find_substitutes: None")
        if candidate is None:
            raise ValueError("Illegal 'candidate' argument in find_substitutes: None")
        if not isinstance(candidate, Atom):
            return set()  # 返回一个空集合

        if candidate.get_identifier() != scheme.get_identifier() or candidate.get_arity() != scheme.get_arity():
            return set()  # 返回一个空集合

        result = set()
        for i in range(scheme.get_arity()):
            term = scheme.get_term(i)
            if term.is_placemarker():
                if term.get_type() == Type.INPUT:
                    result.add(candidate.get_term(i))
            elif isinstance(term, Scheme):
                result.update(SchemeTerm.find_substitutes(term, candidate.get_term(i)))

        return result

    @abstractmethod
    def generalises(self, *args):
        pass





