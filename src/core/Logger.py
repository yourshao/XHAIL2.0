import sys
from os import stat
from colorama import Fore, Style, init

from src.core.Config import Config
from src.core.Dialler import Dialler
from src.core.entities.Answers import Answers


class Logger:
    ANSI_BLACK = Fore.BLACK
    ANSI_BLUE = Fore.BLUE
    ANSI_CYAN = Fore.CYAN
    ANSI_GREEN = Fore.GREEN
    ANSI_PURPLE = Fore.MAGENTA
    ANSI_RED = Fore.RED
    ANSI_RESET = Fore.RESET
    ANSI_WHITE = Fore.WHITE
    ANSI_YELLOW = Fore.YELLOW
    memory = set()
    SIGNATURE = "XHAIL"
    VERSION = "2.0.0"

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


    @staticmethod
    def stamp(answers):
        if answers is None:
            raise ValueError("Illegal 'answers' argument in Logger.stampAnswers(Answers): {answers}")
        else:
            config = answers.get_config()
            if config.is_output():
                print("Problem,Answers,Calls,Loading,Abduction,Deduction,Induction,Wall")
                print(
                    f"completed,{answers.size()},{Dialler.get_calls()},{Answers.get_loading()},{Answers.get_abduction()},"
                    f"{Answers.get_deduction()},{Answers.get_induction()},{Answers.get_now()}")
            else:
                # iterator = iter(answers)
                remaining = 1
                for answer in answers:
                    size = len(answers)
                    if remaining != 1 and (not config.is_all() or size == 0):
                        remaining = len(answers) - 1
                        if not config.is_all() and len(answers) > 0:
                            if not config.is_blind():
                                print(Logger.ANSI_RED, end="")
                            print("NB: ", end="")
                            if not config.is_blind():
                                print(Logger.ANSI_RESET, end="")
                            print(f"{remaining} additional optimal answer/s omitted ", end="")
                            if not config.is_blind():
                                print(Logger.ANSI_WHITE, end="")
                            print(f"(use -a to see them all)\n")

                        break

                    Logger.section(config, f"Answer {remaining}:")

                    if config.is_full():
                        if answer.has_displays():
                            Logger.sub_section(config, "model", answer.get_model(), answer.has_model())
                        Logger.sub_section(config, "delta", answer.get_delta(), answer.has_delta())
                        Logger.sub_section_line(config, "kernel", answer.get_kernel(), answer.has_kernel())
                    Logger.sub_section_line(config, "hypothesis", answer.get_hypotheses(), answer.has_hypotheses())
                    Logger.sub_section(config, "uncovered", answer.get_uncovered(), answer.has_uncovered())
                    if config.is_full():
                        Logger.sub_section(config, "covered", answer.get_covered(), answer.has_covered())

                    print()
                    remaining += 1

                Logger.stat(config, f"Answers     : {answers.count}")
                Logger.stat(config, f"  optimal   : {answers.size()}")
                Logger.stat(config, f"  shown     : {answers.size() if config.all else (0 if answers.is_empty() else 1)}")
                Logger.stat(config, f"Calls       : {Dialler.get_calls()}")
                Logger.stat(config,
                     f"Time        : {Answers.get_now():.3f}s  (loading: {Answers.get_loading():.3f}s  1st answer: {Answers.get_first():.3f}s)")
                Logger.stat(config, f"  abduction : {Answers.get_abduction():.3f}s")
                Logger.stat(config, f"  deduction : {Answers.get_deduction():.3f}s")
                Logger.stat(config, f"  induction : {Answers.get_induction():.3f}s\n")


    @staticmethod
    def section(config, label: str):
        if config is None:
            raise ValueError("Illegal 'config' argument in Logger.stampSection(Config, String): {config}")
        if label is None or (label := label.strip()) == "":
            raise ValueError("Illegal 'label' argument in Utils.stampSection(Config, String): {label}")
        if not config.blind:
            print(Logger.ANSI_RED, end="")
        print(label)


    @staticmethod
    def sub_section(config, label: str, content, determine):
        if config is None:
            raise ValueError("Illegal 'config' argument in Logger.stampSubSection(Config, String, String): {config}")
        if label is None or (label := label.strip()) == "":
            raise ValueError("Illegal 'label' argument in Utils.stampSubSection(Config, String, String): {label}")
        # if content is None:
        #     raise ValueError("Illegal 'content' argument in Logger.stampSubSection(Config, String, String): {content}")
        if not config.blind:
            print(Logger.ANSI_GREEN, end="")
        print(f"  {label}:")
        if not config.blind:
            print(Logger.ANSI_RESET, end="")
        if not determine or content is None:
            print("    -")
        else:
            result = "  ".join(str(line) for line in content)
            print("    " + result)

    @staticmethod
    def sub_section_line(config, label: str, content, determine):
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
        if not determine:
            print("    -")
        else:
            result = "\n    ".join(str(line) for line in content)
            print("     " + result)

    @staticmethod
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
