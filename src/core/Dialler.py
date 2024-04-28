import atexit
import os
import subprocess
import sys
import tempfile
from io import StringIO
from pathlib import Path
from typing import Tuple, Set

from src.core.Buildable import Buildable
import clingo

from src.core.Logger_copy import Logger
from src.core.entities.Values import Values
from src.core.parser.Acquirer import Acquirer


class Dialler:

    class Builder(Buildable):

        config = None
        solvable = None
        source = None
        target = None
        errors = None
        values = None

        def __init__(self, config):
            if config is None:
                raise ValueError(f"Illegal 'config' argument in Dialler.Builder(config, grounding): {config}")
            self.config = config

        def add_grounding(self, grounding):
            if grounding is None:
                raise ValueError(f"Illegal 'grounding' argument in Dialler.Builder(config, grounding): {grounding}")
            self.solvable = grounding
            return self

        def add_values(self, values):
            if values is None:
                raise ValueError(f"Illegal 'values' argument in Dialler.Builder(config, values): {values}")
            self.values = values
            return self

        def add_problem(self, problem):
            if problem is None:
                raise ValueError(f"Illegal 'source' argument in Dialler.Builder(config, source): {problem}")
            self.solvable = problem
            return self

        def build(self):
            return Dialler(self)

    ERROR = "ERROR: "
    WARNING = "% warning: "
    calls = 0

    def __init__(self, builder):

        self.config = builder.config
        self.solvable = builder.solvable
        self.values = builder.values
        self.debug = builder.config.debug
        self.mute = builder.config.mute
        self.output = builder.config.output
        self.paths = {
            'source': Path(tempfile.mkstemp(prefix='xhail', suffix='.tmp')[1]),
            'target': Path(tempfile.mkstemp(prefix='xhail', suffix='.tmp')[1]),
            'errors': Path(tempfile.mkstemp(prefix='xhail', suffix='.tmp')[1]),
        }
        for path in self.paths.values():
            atexit.register(os.remove, path)

    @staticmethod
    def get_calls():
        return Dialler.calls

    def execute(self, iter: int):
        if iter < 0:
            raise ValueError("Illegal 'iter' argument in Dialler.execute(int): {}".format(iter))
        Dialler.calls += 1
        try:
            self.solvable.save(iter, self.paths['source'])  # Assuming save() returns a file path to the logic program.

            # Running Clingo with the provided logic program
            try:
                with open(self.paths['source'], 'r', encoding='utf-8') as source_file:
                    source = source_file.read()

                with open(self.paths['errors'], 'w', encoding='utf-8') as error_file, open(self.paths['target'], 'w') as target_file:
                    result = subprocess.run(
                        ['clingo', '--verbose=0'],
                        # '--opt-bound=builder.value.tostring'
                        input=source,
                        stdout=target_file,
                        stderr=error_file,
                        text=True
                    )
                source_file.close()
                try:
                    self.handle(self.paths['errors'])
                except Exception as e:
                    Logger.error("Error during error handling: {}".format(str(e)))
                try:
                    with open(self.paths['target'], 'r') as target_file:
                        # if iter >0:
                        target = Acquirer.from_stream(target_file).parse()
                        target_file.close()
                    return target

                except Exception as e:
                    Logger.error(f"Error during target acquisition: {str(e)}")
            except FileNotFoundError:
                Logger.error("Cannot find 'clingo' executable")
                return None
        except IOError:
            Logger.error("Cannot write to 'clingo' process")
            return None
        return {None: {None}}


    def handle(self, errors_file: Path):
        try:
            with open(errors_file, 'r') as f:
                message = ""
                for line in f:
                    line = line.strip()
                    if line:
                        if message:
                            message += "\n  " + line
                        elif line.startswith(self.ERROR):
                            message = line[len(self.ERROR):]
                        elif line.startswith(self.WARNING):
                            content = line[len(self.WARNING):]
                            if content not in ("bad_solution/0 is never defined", "number_abduced/2 is never defined"):
                                Logger.warning(self.mute, content)
                        else:
                            print(line, file=sys.stderr)
                if message:
                    Logger.error(message)
        except IOError:
            Logger.error("cannot read from child process' 'stderr'")
