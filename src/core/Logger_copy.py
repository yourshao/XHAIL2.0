import sys
from os import stat

from src.core.Config import Config


class Logger:
    ANSI_BLACK = "\033[30m"
    ANSI_BLUE = "\033[34m"
    ANSI_CYAN = "\033[36m"
    ANSI_GREEN = "\033[32m"
    ANSI_PURPLE = "\033[35m"
    ANSI_RED = "\033[31m"
    ANSI_RESET = "\033[0m"
    ANSI_WHITE = "\033[37m"
    ANSI_YELLOW = "\033[33m"
    memory = set()
    SIGNATURE = "xhail"
    VERSION = "0.5.1"

    @staticmethod
    def clear():
        Logger.memory.clear()

    @staticmethod
    def error(message):
        if message:
            print(f"{Logger.ANSI_RED}*** ERROR ({Logger.SIGNATURE}): {message}{Logger.ANSI_RESET}")
            print(f"{Logger.ANSI_WHITE}*** Info  ({Logger.SIGNATURE}): try '-h' or '--help' for usage information{Logger.ANSI_RESET}")
            raise SystemExit(-1)

    @staticmethod
    def found(config):
        if config is None:
            raise ValueError("Illegal 'application' argument in Logger.found(Config): None")
        # Assume Config has methods getGringo() and getClasp() that return paths
        print(f"Using '{config.getGringo()}'...")
        print(f"Using '{config.getClasp()}'...")
        print()
        print("Next time try to invoke the application with the following parameters:")
        params = f"  python -m {Logger.SIGNATURE}.py -c {config.getClasp()} -g {config.getGringo()}"
        print(params)
        # Add additional config details here

    @staticmethod
    def version():
        print()
        print(f"{Logger.SIGNATURE} {Logger.VERSION}")
        print("This is free software under the GPL v3 license.")

    @staticmethod
    def warning(mute, message):
        if message and not mute and message not in Logger.memory:
            Logger.memory.add(message)
            print(f"{Logger.ANSI_YELLOW}* Warning ({Logger.SIGNATURE}): {message}{Logger.ANSI_RESET}")

    @staticmethod
    def message(message):
        if message:
            print(f"{Logger.ANSI_BLUE}*** Info  ({Logger.SIGNATURE}): {message}{Logger.ANSI_RESET}")


    # @staticmethod
    # def stamp(answers):
    #     if answers is None:
    #         raise ValueError("Illegal 'answers' argument in Logger.stampAnswers(Answers): {answers}")
    #     config = answers.config
    #     if config.output:
    #         print("Problem,Answers,Calls,Loading,Abduction,Deduction,Induction,Wall")
    #         print(
    #             f"completed,{len(answers)},{Dialler.calls},{answers.loading:.3f},{answers.abduction:.3f},{answers.deduction:.3f},{answers.induction:.3f},{answers.now:.3f}",
    #             file=sys.stderr)
    #     else:
    #         iterator = iter(answers)
    #         print(answers.get_answers())
    #         if next(iterator, None) is not None:
    #             print(1)
    #             for id in range(1, len(answers) + 1):
    #                 answer = next(iterator)
    #                 Logger.section(config, f"Answer {id}:")
    #                 if config.full:
    #                     if answer.displays:
    #                         Logger.sub_section(config, "model", " ".join(answer.model) if answer.model else "-")
    #                         Logger.sub_section(config, "delta", " ".join(answer.delta) if answer.delta else "-")
    #                         Logger.sub_section(config, "kernel", "\n    ".join(answer.kernel) if answer.kernel else "-")
    #                     Logger.sub_section(config, "hypothesis", "\n    ".join(answer.hypotheses) if answer.hypotheses else "-")
    #                     Logger.sub_section(config, "uncovered", " ".join(answer.uncovered) if answer.uncovered else "-")
    #                     if config.full:
    #                         Logger.sub_section(config, "covered", " ".join(answer.covered) if answer.covered else "-")
    #                 print()
    #             remaining = len(answers) - 1
    #             if not config.all and remaining > 0:
    #                 if not config.blind:
    #                     print(Logger.ANSI_RED, end="")
    #                 print("NB: ", end="")
    #                 if not config.blind:
    #                     print(Logger.ANSI_RESET, end="")
    #                 print(f"{remaining} additional optimal answer/s omitted ", end="")
    #                 if not config.blind:
    #                     print(Logger.ANSI_WHITE, end="")
    #                 print(f"(use {A} to see them all)\n")
    #         print(answers.count())
    #         Logger.stat(config, f"Answers     : {answers.count()}")
    #         print(1)
    #         Logger.stat(config, f"  optimal   : {len(answers)}")
    #         Logger.stat(config, f"  shown     : {len(answers) if config.all else (0 if not answers else 1)}")
    #         print(3)
    #         Logger.stat(config, f"Calls       : {Dialler.calls}")
    #         Logger.stat(config,
    #              f"Time        : {answers.now:.3f}s  (loading: {answers.loading:.3f}s  1st answer: {answers.first:.3f}s)")
    #         Logger.stat(config, f"  abduction : {answers.abduction:.3f}s")
    #         Logger.stat(config, f"  deduction : {answers.deduction:.3f}s")
    #         Logger.stat(config, f"  induction : {answers.induction:.3f}s\n")

    def section(config, label: str):
        if config is None:
            raise ValueError("Illegal 'config' argument in Logger.stampSection(Config, String): {config}")
        if label is None or (label := label.strip()) == "":
            raise ValueError("Illegal 'label' argument in Utils.stampSection(Config, String): {label}")
        if not config.blind:
            print(Logger.ANSI_RED, end="")
        print(label)

    def sub_section(config, label: str, content: str):
        if config is None:
            raise ValueError("Illegal 'config' argument in Logger.stampSubSection(Config, String, String): {config}")
        if label is None or (label := label.strip()) == "":
            raise ValueError("Illegal 'label' argument in Utils.stampSubSection(Config, String, String): {label}")
        if content is None:
            raise ValueError("Illegal 'content' argument in Logger.stampSubSection(Config, String, String): {content}")
        if not config.blind:
            print(Logger.ANSI_GREEN, end="")
        print(f"  {label}:")
        if not config.blind:
            print(Logger.ANSI_RESET, end="")
        if not content:
            print("    -")
        else:
            print("    " + content)

    def stat(config, value: str):
        if config is None:
            raise ValueError("Illegal 'config' argument in Logger.stampStat(Config, String): {config}")
        if value is None:
            raise ValueError("Illegal 'value' argument in Utils.stampStat(Config, String): {value}")
        if not config.blind:
            print(Logger.ANSI_CYAN, end="")
        print(value)



    #
    # try:
    #     Logger.error("An example error.")
    # except SystemExit as e:
    #     pass
