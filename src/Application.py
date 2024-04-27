import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from typing import Callable

import clingo
import argparse
from core.Config import Config
from src.core import Utils
from src.core.Dialler import Dialler
from src.core.Finder import Finder
from src.core.Logger import Logger
from src.core.entities.Answers import Answers
from src.core.entities.Problem import Problem


class Application(Callable):
    PATHS = []
    ROOT = None
    service = None
    config = None
    problem = None



    def __init__(self, config: Config):
        if config is None:
            raise ValueError("Config cannot be None")
        self.config = config
        if config.is_version():
            Logger.version()

        problem = Problem.Builder(config)
        if config.has_sources():
            var9 = config.get_sources()
            for path in var9:
                Logger.message(f"Reading source file: {path}")
                # this step is to parse the source file, and then build the problem
                problem.parse(path)

        else:
            Logger.message("Reading source file from standard input")
            problem.parse(sys.stdin)

        self.problem = problem.build()
        Answers.started()
        Answers.loaded()

    def __call__(self):
        Logger.message("Solving ...")
        answers = self.problem.solve()
        return answers

    def execute(self):
        if self.config.prettify:
            Utils.dump(self.problem, sys.stderr)
        else:
            kill = self.config.get_kill()
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    task = executor.submit(self)
                    answers = task.result(timeout=kill) if kill else task.result()
                    Logger.stamp(answers)
            except concurrent.futures.CancelledError:
                Logger.message(f"*** Info  (xhail): computation was cancelled")
            except concurrent.futures.TimeoutError:
                Logger.message(f"*** Info  (xhail): solving interrupted after {kill} second/s")
                if config.isOutput():
                    print("Problem,Answers,Calls,Loading,Abduction,Deduction,Induction,Wall")
                    print(f"interrupted,{self.problem.count()},{Dialler.calls()},..."
                          f"{Answers.get_loading()}, {Answers.get_abduction()},"          
                          f"{Answers.get_deduction()}, {Answers.get_induction()}, {float(kill)}")
            except concurrent.futures.TimeoutError as e:
                Logger.message(f"*** Info  (xhail): computation timed out: {str(e)}")
            except concurrent.futures.CancelledError as e:
                Logger.message(f"*** Info  (xhail): computation was cancelled: {str(e)}")
            except Exception as e:
                Logger.message(f"*** Info  (xhail): unexpected error occurred: {str(e)}")





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sample Application with detailed configuration.')
    parser.add_argument('-a', '--all', action='store_true', help='Print all the best answers')
    parser.add_argument('-b', '--blind', action='store_true', help='Remove colours from the program output')
    parser.add_argument('-d', '--debug', action='store_true', help='Leave temporary files in ./temp')
    parser.add_argument('-f', '--full', action='store_true', help='Show a more detailed output')
    # 这是一个例子，说明如何通过命令行输入路径
    parser.add_argument('-i', '--iterations', type=int, help='Run <num> iterations for non-minimal answers')
    parser.add_argument('-k', '--kill', type=int, help='Stop the program after <num> seconds')
    parser.add_argument('-m', '--mute', action='store_true', help='Suppress warning messages')
    parser.add_argument('-o', '--output', action='store_true', help='Output flag')
    parser.add_argument('-p', '--prettify', action='store_true', help='Nicely format current problem')
    parser.add_argument('-s', '--search', action='store_true', help='Search for clasp and gringo')
    # 特别的函数，停止之后应该等待输入，自动开启后面加入的功能
    parser.add_argument('-t', '--terminate', action='store_true', help='halt searching hypotheses after first match')
    parser.add_argument('-v', '--version', action='store_true', help='Print version information and exit')

    parser.add_argument('-c', '--change', type=int, help='define total amount of steps')
    parser.add_argument('-n', '--threads', type=int, help='define amount of threads to be utilized')
    parser.add_argument('-e', '--atom', nargs=2, action='append', metavar=('KEY', 'VALUE'), help='Set truth value for a given atom (e.g., --truth atom True).')

    # parser.add_argument('-e', '--atom', type=str, help='define which atom and what value need be changed')
    # 不知道这里是不是需要规定几行和几列，但是目前是没有这么复杂的构造，如果后续证明必须要可以再添加。
    parser.add_argument('-x', '--ast', action='append', help='define new predict to atom')

    # 这是一个储存了源文件的位置
    parser.add_argument('sources', nargs='*', help='Source file paths')

    args = parser.parse_args()
    builder = Config.Builder()
    (builder.set_all(args.all)
    .set_blind(args.blind)
    .set_debug(args.debug)
    .set_full(args.full)
    .set_iterations(args.iterations)
    .set_kill(args.kill)
    .set_mute(args.mute)
    .set_output(args.output)
    .set_prettify(args.prettify)
    .set_search(args.search)
    .set_terminate(args.terminate)
    .set_version(args.version)
     .set_threads(args.threads)
     .add_source(args.sources))
    if args.atom:
        for key, value in args.atom:
            builder.set_atom_values(key, (value == 'True' or value == 'true'))
    builder.add_ast_rule(args.ast)
    config = builder.build()

# 运行部分在这里，还没有写，我感觉大概是把config放在里面就可以了

    app = Application(config)
    app.execute()


    # with open(config.sources[0], 'r') as file:
    #     content = file.read()
    #     print(content)
    #
