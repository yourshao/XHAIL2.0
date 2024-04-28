from abc import ABC
from pathlib import Path
from typing import List

from src.core import Utils
from src.core.Buildable import Buildable
from src.core.Dialler import Dialler
from src.core.LinkedHashSet import LinkedHashSet
from src.core.Logger_copy import Logger
from src.core.entities.Answers import Answers
from src.core.entities.Solvable import Solvable
from collections import OrderedDict

from src.core.entities.Values import Values
from src.core.parser.InputStates import InputStates
from src.core.parser.Parser import Parser
from src.core.parser.Splitter import Splitter
from src.core.statements.Display import Display
from src.core.statements.Example import Example
from src.core.statements.ModeB import ModeB
from src.core.statements.ModeH import ModeH
from sortedcontainers import SortedSet

from src.core.terms.Atom import Atom


class Problem(Solvable):
    background: [str] = []
    config = None
    displays: [Display] = []
    domains: [str]= []
    examples: [Example] = []
    lookup = {}
    modeBs: [ModeB] = []
    modeHs: [ModeH] = []
    refinements = set()


    def __init__(self, builder):
        self.background: [str] = []
        self.config = None
        self.displays: [Display] = []
        self.domains: [str]= []
        self.examples: [Example] = []
        self.lookup = {}
        self.modeBs: [ModeB] = []
        self.modeHs: [ModeH] = []
        self.refinements = set()

        self.refinements = set()
        self.count = 0
        if builder is None:
            raise ValueError(f"Illegal 'builder' argument in Problem(builder): {builder}")
        else:
            self.background = list(builder.background)
            self.config = builder.config
            self.displays = list(builder.displays)
            self.domains = list(builder.domains)
            self.examples = list(builder.examples)
            self.lookup = builder.lookup
            self.modeBs = list(builder.modeBs)
            self.modeHs = list(builder.modeHs)

    def __eq__(self, other):
        if not isinstance(other, Problem):
            return False
        if self.background != other.background:
            return False
        if self.config != other.config:
            return False
        if self.displays != other.displays:
            return False
        if self.domains != other.domains:
            return False
        if self.examples != other.examples:
            return False
        if self.lookup != other.lookup:
            return False
        if self.modeBs != other.modeBs:
            return False
        if self.modeHs != other.modeHs:
            return False
        if self.refinements != other.refinements:
            return False
        return True

    def get_background(self) -> List[str]:
        return self.background

    def get_config(self):
        return self.config

    def get_displays(self) -> List[Display]:
        return self.displays

    def get_domains(self) -> List[str]:
        return self.domains

    def get_examples(self) -> List[Example]:
        return self.examples

    def get_filters(self):
        result = SortedSet()
        # result.add("#hide.")

        for display in self.displays:
            result.add(f"#show {display.get_identifier()}/{display.get_arity()}.")

        for example in self.examples:
            result.add(f"#show {example.get_atom().get_identifier()}/{example.get_atom().get_arity()}.")

        for mode in self.modeHs:
            scheme = mode.get_scheme()
            result.add(f"#show {scheme.get_identifier()}/{scheme.get_arity()}.")
            result.add(f"#show abduced_{scheme.get_identifier()}/{scheme.get_arity()}.")
            for placemarker in scheme.get_placemarkers_0():
                result.add(f"#show {placemarker.get_identifier()}/1.")
        for mode in self.modeBs:
            scheme = mode.get_scheme()
            result.add(f"#show {scheme.get_identifier()}/{scheme.get_arity()}.")
            for placemarker in scheme.get_placemarkers_0():
                result.add(f"#show {placemarker.get_identifier()}/1.")
        return result

    def get_modeBs(self):
        return self.modeBs

    def get_modeHs(self):
        return self.modeHs

    def get_refinements(self):
        return self.refinements

    def has_background(self):
        return len(self.background) > 0

    def has_displays(self):
        return len(self.displays) > 0

    def has_domains(self):
        return len(self.domains) > 0

    def has_examples(self):
        return len(self.examples) > 0

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + hash(tuple(self.background))
        result = prime * result + (0 if self.config is None else hash(self.config))
        result = prime * result + hash(tuple(self.displays))
        result = prime * result + hash(tuple(self.domains))
        result = prime * result + hash(tuple(self.examples))
        result = prime * result + (0 if self.lookup is None else hash(tuple(self.lookup)))
        result = prime * result + hash(tuple(self.modeBs))
        result = prime * result + hash(tuple(self.modeHs))
        result = prime * result + (0 if self.refinements is None else hash(tuple(self.refinements)))
        return result

    def has_modes(self) -> bool:
        return len(self.modeBs) > 0 or len(self.modeHs) > 0

    def look_up(self, atom: Atom) -> bool:
        if atom is None:
            raise ValueError("Illegal 'atom' argument in Problem.lookup(Atom): " + str(atom))
        key = atom.get_identifier()
        if key not in self.lookup:
            return False
        return atom.get_arity() in self.lookup[key]

    def save(self, iter: int, stream) -> bool:
        return Utils.save(self, iter, stream)

    def count(self) -> int:
        return self.count

    def solve(self) -> Answers:
        builder = Answers.Builder(self.config)
        if len(self.background) > 0 or len(self.examples) > 0 or len(self.modeHs) > 0 or len(self.modeBs) > 0:
            iters = 0
            generalisations = LinkedHashSet()
            while not builder.is_meaningful() and iters <= self.config.get_iterations():
                if self.config.debug:
                    Utils.save_temp(self, iters, Path(f"{self.config.name}_abd{iters}.lp"))
                iit = 0
                values = Values()
                dialler = Dialler.Builder(self.config).add_problem(self).build()
                entry = Answers.time_abduction(iters, dialler)
                for ver8 in entry.values():
                    for output in ver8:
                        # output = next(output)
                        self.count = builder.size()
                        if builder.size() > 0 and self.config.is_terminate():
                            break
                        grounding = Answers.time_deduction(self, output)
                        if self.config.debug:
                            Logger.message(f"*** Info  ({Logger.SIGNATURE}): found Delta: {grounding.get_delta()}")
                            Logger.message(f"*** Info  ({Logger.SIGNATURE}): found Kernel: {grounding.get_kernel()}")
                            Logger.message(f"*** Info  ({Logger.SIGNATURE}): found Generalisation: {grounding.get_generalisation()}")
                            if grounding.needs_induction():
                                Utils.save_temp(grounding, iters, Path(f"{self.config.name}_abd{iters}_ind{iit}.lp"))
                        generalisation = set(grounding.get_generalisation())
                        if generalisation not in generalisations:
                            values = grounding.solve(values, builder)
                            self.refinements.add(grounding.as_bad_solution())
                            generalisations.add(generalisation)
                        self.count = builder.size()
                    iters += 1
            if builder.size() > 0 and self.config.terminate:
                print(f"*** Info  ({Logger.SIGNATURE}): search for hypotheses terminated after the first match")
            if not builder.is_meaningful():
                print(f"*** Info  ({Logger.SIGNATURE}): no meaningful answers, try more iterations (--iter,-i <num>)")
        return builder.build()

    def __str__(self) -> str:
        return f"Problem [\n  background={self.background},\n  config={self.config},\n  displays={self.displays},\n  domains={self.domains},\n  examples={self.examples},\n  modeBs={self.modeBs},\n  modeHs={self.modeHs}\n]"

    class Builder(Buildable):
        background = LinkedHashSet()
        config = None
        displays = LinkedHashSet()
        domains = LinkedHashSet()
        examples = LinkedHashSet()
        lookup = {}
        modeBs = LinkedHashSet()
        modeHs = LinkedHashSet()

        def __init__(self, config):
            if config is None:
                raise ValueError(f"Illegal 'config' argument in Problem.Builder(config): {config}")
            self.config = config

        def add_background(self, statement: str):
            if statement is not None:
                statement = statement.strip()
                if statement.startswith("#compute"):
                    Logger.warning(self.config.mute, "'#compute' statements are not supported and will be ignored")
                elif statement.startswith("#hide"):
                    Logger.warning(self.config.mute, "'#hide' statements are not supported and will be ignored")
                elif statement.startswith("#show"):
                    Logger.warning(self.config.mute, "'#show' statements are not supported and will be ignored")
                elif statement.startswith("#display") and statement.endswith("."):
                    display = statement[len("#display"): -1].strip()
                    self.add_display(Parser.parse_display_1(display))
                elif statement.startswith("#example") and statement.endswith("."):
                    example = statement[len("#example"): -1].strip()
                    self.add_example(Parser.parse_example_1(example))
                elif statement.startswith("#modeb") and statement.endswith("."):
                    modeb = statement[len("#modeb"): -1].strip()
                    self.add_modeB(Parser.parse_modeB_1(modeb))
                elif statement.startswith("#modeh") and statement.endswith("."):
                    modeh = statement[len("#modeh"): -1].strip()
                    self.add_modeH(Parser.parse_modeH_1(modeh))
                elif statement.startswith("#domain"):
                    self.domains.add(statement)
                else:
                    self.background.add(statement)
            return self

        def add_display(self, display: Display) -> 'Problem.Builder':
            if display is None:
                raise ValueError(f"Illegal 'display' argument in Problem.Builder.add_display(Display): {display}")
            self.displays.add(display)
            return self

        def add_example(self, example:Example) -> 'Problem.Builder':
            if example is not None:
                self.examples.add(example)
            return self

        def add_modeB(self, modeB: ModeB) -> 'Problem.Builder':
            if modeB is not None:
                self.modeBs.add(modeB)
            return self

        def add_modeH(self, modeH: ModeH) -> 'Problem.Builder':
            if modeH is not None:
                self.modeHs.add(modeH)
            return self

        def build(self) -> 'Problem':
            self.lookup.clear()

            for display in self.displays:
                key = display.get_identifier()
                arities = self.lookup.get(key)
                if arities is None:
                    arities = set()
                    self.lookup[key] = arities
                arities.add(display.get_arity())
            return Problem(self)

        def clear(self) -> 'Problem.Builder':
            self.background.clear()
            self.displays.clear()
            self.examples.clear()
            self.lookup.clear()
            self.modeBs.clear()
            self.modeHs.clear()
            return self

        def clear_displays(self) -> 'Problem.Builder':
            self.displays.clear()
            self.lookup.clear()
            return self

        def clear_examples(self) -> 'Problem.Builder':
            self.examples.clear()
            return self

        def clear_modeBs(self) -> 'Problem.Builder':
            self.modeBs.clear()
            return self

        def clear_modeHs(self) -> 'Problem.Builder':
            self.modeHs.clear()
            return self

        def __eq__(self, other):
            if not isinstance(other, Problem.Builder):
                return False

            return (self.background == other.background and
                    self.config == other.config and
                    self.displays == other.displays and
                    self.domains == other.domains and
                    self.examples == other.examples and
                    self.lookup == other.lookup and
                    self.modeBs == other.modeBs and
                    self.modeHs == other.modeHs)

        def __hash__(self):
            prime = 31
            result = 1
            result = prime * result + (0 if self.background is None else hash(self.background))
            result = prime * result + (0 if self.config is None else hash(self.config))
            result = prime * result + (0 if self.displays is None else hash(self.displays))
            result = prime * result + (0 if self.domains is None else hash(self.domains))
            result = prime * result + (0 if self.examples is None else hash(self.examples))
            result = prime * result + (0 if self.lookup is None else hash(self.lookup))
            result = prime * result + (0 if self.modeBs is None else hash(self.modeBs))
            result = prime * result + (0 if self.modeHs is None else hash(self.modeHs))
            return result

        def parse(self, stream):
            if stream is None:
                raise ValueError(f"Illegal 'stream' argument in Problem.Builder.parse(InputStream): {stream}")
            else:
                if isinstance(stream, str):
                    with open(stream, 'r') as file:
                        for statement in Splitter(InputStates.INITIAL).parse(file):
                            self.add_background(statement)
                else:
                    for iter in Splitter(InputStates.INITIAL).parse(stream):
                        self.add_background(iter)
                return self

        # def parse(self, source):
        #     source = Path(source)
        #     if isinstance(source, Path):
        #         try:
        #             input_bytes = source.read_bytes()
        #         except FileNotFoundError as e:
        #             Logger.error("Cannot find file '" + source.name + "'")
        #             return self
        #     elif hasattr(source, 'buffer'):  # This checks if it's sys.stdin or similar
        #         input_bytes = source.buffer.read()
        #     else:
        #         raise ValueError("Unsupported source type provided to parse method.")
        #
        #     self.parse_from_bytes(input_bytes)
        #
        #     return self

        def remove_background(self, statement: str) -> 'Problem.Builder':
            if statement:
                statement = statement.strip()
                if not (statement.startswith("#compute") or statement.startswith("#hide") or statement.startswith("#show")):
                    if statement.startswith("#display") and statement.endswith("."):
                        display = Parser.parse_display_1(statement[len("#display"):-1].strip())
                        self.remove_display(display)
                    elif statement.startswith("#example") and statement.endswith("."):
                        example = Parser.parse_example_1(statement[len("#example"):-1].strip())
                        self.remove_example(example)
                    elif statement.startswith("#modeb") and statement.endswith("."):
                        modeB = Parser.parse_modeB_1(statement[len("#modeb"):-1].strip())
                        self.remove_modeB(modeB)
                    elif statement.startswith("#modeh") and statement.endswith("."):
                        modeH = Parser.parse_modeH_1(statement[len("#modeh"):-1].strip())
                        self.remove_modeH(modeH)
                    elif statement.startswith("#domain"):
                        self.domains.remove(statement)
                    else:
                        self.background.remove(statement)
            return self


        def remove_display(self, display: Display) -> 'Problem.Builder':
            if display is None:
                raise ValueError(f"Illegal 'display' argument in Problem.Builder.remove_display(Display): {display}")
            self.displays.remove(display)
            return self

        def remove_example(self, example: Example) -> 'Problem.Builder':
            if example is None:
                raise ValueError(f"Illegal 'example' argument in Problem.Builder.remove_example(Example): {example}")
            self.examples.remove(example)
            return self

        def remove_modeB(self, modeB: ModeB) -> 'Problem.Builder':
            if modeB is None:
                raise ValueError(f"Illegal 'modeB' argument in Problem.Builder.remove_modeB(ModeB): {modeB}")
            self.modeBs.remove(modeB)
            return self

        def remove_modeH(self, modeH: ModeH) -> 'Problem.Builder':
            if modeH is None:
                raise ValueError(f"Illegal 'modeH' argument in Problem.Builder.remove_modeH(ModeH): {modeH}")
            self.modeHs.remove(modeH)
            return self


        def parse_from_bytes(self, input_bytes):
            # Example parsing logic
            data = input_bytes.decode('utf-8')  # Decode bytes to a string
            for line in data.splitlines():
                self.add_background(line)

    def is_problem(self):
        return True


