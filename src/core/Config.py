import os

from src.core.Buildable import Buildable


class Config:
    all = False
    blind = False
    debug = False
    full = False
    help = False
    iterations = 0
    kill = 0
    mute = False
    output = False
    prettify = False
    search = False
    sources = []
    terminate = False
    version = False
    atom_values = []
    threads = 1
    ast_rules = []

    def __init__(self):
        pass

    class Builder(Buildable):
        def __init__(self):
            self.errors = ""
            self.config = Config()

        def set_all(self, value):
            self.config.all = value
            return self

        def set_blind(self, value):
            self.config.blind = value
            return self


        def set_debug(self, value):
            self.config.debug = value
            return self

        def set_full(self, value):
            self.config.full = value
            return self

        def set_help(self, value):
            self.config.help = value
            return self

        def set_iterations(self, value):
            if value is not None:
                self.config.iterations = value
            return self

        def set_kill(self, value):
            self.config.kill = value
            return self

        def set_mute(self, value):
            self.config.mute = value
            return self

        def set_output(self, value):
            self.config.output = value
            return self

        def set_prettify(self, value):
            self.config.prettify = value
            return self

        def set_search(self, value):
            self.config.search = value
            return self

        def add_source(self, sources):
            if sources is None:
                raise ValueError(f"Illegal 'source' argument in Application.Builder.addSource(Path): {source}")

            # 使用 os.path 来处理路径
            for source in sources:
                temp = os.path.abspath(source)

                # 检查文件是否存在且不是目录
                if os.path.exists(temp) and not os.path.isdir(temp):
                    self.config.sources.append(temp)
                # 检查文件是否可读
                elif os.access(temp, os.R_OK):
                    self.errors += f"  file '{source}' cannot be accessed\n"
                else:
                    self.errors += f"  unknown argument '{source}'\n"

            return self

        def set_terminate(self, value):
            self.config.terminate = value
            return self

        def set_version(self, value):
            self.config.version = value
            return self

        def set_atom_values(self, key, value):
            self.config.atom_values[key] = value
            return self

        def set_threads(self, value):
            self.config.threads = value
            return self

        # 应该想多数怎么半办

        def add_ast_rule(self, rule):
            if rule is not None:
                self.config.ast_rules = rule
            return self

        def build(self):
            return self.config

    def is_version(self):
        return self.version

    def get_iterations(self):
        return self.iterations

    def get_kill(self):
        return self.kill
    #
    # def get_name(self):
    #     return self.name

    def get_sources(self):
        return self.sources

    def has_sources(self):
        return len(self.sources) > 0

    def is_all(self):
        return self.all

    def is_blind(self):
        return self.blind

    def is_debug(self):
        return self.debug

    def is_full(self):
        return self.full

    def is_help(self):
        return self.help

    def is_mute(self):
        return self.mute

    def is_output(self):
        return self.output

    def is_prettify(self):
        return self.prettify

    def is_search(self):
        return self.search

    def is_terminate(self):
        return self.terminate









