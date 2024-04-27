import os
from pathlib import Path
from typing import Union
from src.core.Logger_copy import Logger


def dump(problem, stream):
    if problem is None:
        raise ValueError("Illegal 'problem' argument in Utils.save(Problem, OutputStream): None")
    if stream is None:
        raise ValueError("Illegal 'stream' argument in Utils.save(Problem, OutputStream): None")
    try:
        printer = stream
        if problem.has_displays():
            for display in problem.get_displays():
                printer.write(str(display) + "\n")
            printer.write("\n")
        if problem.has_background() or problem.has_domains():
            printer.write("%% B. Background\n")
            for statement in problem.get_domains():
                printer.write(statement + "\n")
            for statement in problem.get_background():
                printer.write(statement + "\n")
            printer.write("\n")
        if problem.has_examples():
            printer.write("%% E. Examples\n")
            for example in problem.get_examples():
                printer.write(str(example) + "\n")
            printer.write("\n")
        if problem.has_modes():
            printer.write("%% M. Modes\n")
            for mode in problem.get_mode_hs():
                printer.write(str(mode) + "\n")
            for mode in problem.get_mode_bs():
                printer.write(str(mode) + "\n")
            printer.write("\n")
        return True
    except Exception as e:
        Logger.error("cannot stream data to process")
    return False


def save(solvable, iter, stream):
    if solvable.is_problem() is True:
        problem = solvable

        if problem is None:
            raise ValueError("Illegal 'problem' argument in Utils.save(Problem, int, OutputStream): None")
        if iter < 0:
            raise ValueError("Illegal 'iter' argument in Utils.save(Problem, int, OutputStream): " + str(iter))
        if stream is None:
            raise ValueError("Illegal 'stream' argument in Utils.save(Problem, int, OutputStream): None")

        with open(stream, 'w') as printer:
            for filter in problem.get_filters():
                printer.write(filter + "\n")
            printer.write("\n")
            printer.write("%%% B. Background\n")
            for statement in problem.get_domains():
                printer.write(statement + "\n")
            for statement in problem.get_background():
                printer.write(statement + "\n")
            for refinement in problem.get_refinements():
                printer.write(refinement + "\n")
            printer.write("\n")
            printer.write("%%% E. Examples\n")
            for example in problem.get_examples():
                for statement in example.as_clauses():
                    printer.write(statement + "\n")
            printer.write("\n")
            printer.write("%%% I. Inflation\n")
            if iter > 0:
                printer.write(":-bad_solution.\n")
                printer.write("number_abduced(V):-V = #sum{ W : number_abduced(_,W) }.\n")
            for mode in problem.get_modeHs():
                for statement in mode.as_clauses():
                    if iter > 0 or not statement.startswith("number_abduced("):
                        printer.write(statement + "\n")
        printer.close()
        return True
    else:
        grounding = solvable
        if grounding is None:
            raise ValueError("Illegal 'grounding' argument in Utils.save(Grounding, int, OutputStream): None")
        if iter < 0:
            raise ValueError("Illegal 'iter' argument in Utils.save(Grounding, int, OutputStream): " + str(iter))
        if stream is None:
            raise ValueError("Illegal 'stream' argument in Utils.save(Grounding, int, OutputStream): None")
        try:
            printer = stream
            for filter in grounding.get_filters():
                printer.write(filter + "\n")
            printer.write("\n")
            printer.write("%%% B. Background\n")
            for statement in grounding.get_domains():
                printer.write(statement + "\n")
            for statement in grounding.get_background():
                printer.write(statement + "\n")
            printer.write("\n")
            printer.write("%%% E. Examples\n")
            for example in grounding.get_examples():
                for statement in example.as_clauses():
                    printer.write(statement + "\n")
            printer.write("\n")
            printer.write("%%% C. Compression\n")
            for statement in grounding.as_clauses():
                printer.write(statement + "\n")
            printer.write("\n")
            printer.close()
            return True
        except Exception as e:
            Logger.error("cannot stream data to process")
        return False
#
#
# def save(problem, iter, file_path):
#     if problem is None:
#         raise ValueError("Illegal 'problem' argument in Utils.save(Problem, int, OutputStream): None")
#     if iter < 0:
#         raise ValueError("Illegal 'iter' argument in Utils.save(Problem, int, OutputStream): " + str(iter))
#     if file_path is None:
#         raise ValueError("Illegal 'stream' argument in Utils.save(Problem, int, OutputStream): None")
#
#     with open(file_path, 'w') as printer:
#         for filter in problem.getFilters():
#             printer.write(filter + "\n")
#         printer.write("\n")
#         printer.write("%%% B. Background\n")
#         for statement in problem.getDomains():
#             printer.write(statement + "\n")
#         for statement in problem.getBackground():
#             printer.write(statement + "\n")
#         for refinement in problem.getRefinements():
#             printer.write(refinement + "\n")
#         printer.write("\n")
#         printer.write("%%% E. Examples\n")
#         for example in problem.getExamples():
#             for statement in example.as_clauses():
#                 printer.write(statement + "\n")
#         printer.write("\n")
#         printer.write("%%% I. Inflation\n")
#         if iter > 0:
#             printer.write(":-bad_solution.\n")
#             printer.write("number_abduced(V):-V:=#sum[ number_abduced(_,W) =W ].\n")
#         for mode in problem.getModeHs():
#             for statement in mode.asClauses():
#                 if iter > 0 or not statement.startswith("number_abduced("):
#                     printer.write(statement + "\n")
#     return True
#

def save_temp(grounding, iter, path: Union[str, Path]):
    if grounding is None:
        raise ValueError("Illegal 'grounding' argument in Utils.save(Grounding, int, Path): None")
    if iter < 0:
        raise ValueError("Illegal 'iter' argument in Utils.save(Grounding, int, Path): " + str(iter))
    if path is None:
        raise ValueError("Illegal 'path' argument in Utils.save(Grounding, int, Path): None")
    try:
        temp_dir = Path(".", "temp").resolve()
        if not temp_dir.exists():
            os.makedirs(temp_dir)
        file_path = temp_dir / path.name
        try:
            with open(file_path, "w") as file:
                return save(grounding, iter, file)
        except IOError:
            Logger.error(f"cannot write to '{path.name}' file (do we have rights?)")
    except IOError:
        Logger.warning(False, "cannot create 'temp' folder (do we have rights?)")
    return False


def save_temp(problem, iter, path: Union[str, Path]):
    if problem is None:
        raise ValueError("Illegal 'problem' argument in Utils.save(Problem, int, Path): None")
    if iter < 0:
        raise ValueError("Illegal 'iter' argument in Utils.save(Problem, int, Path): " + str(iter))
    if path is None:
        raise ValueError("Illegal 'path' argument in Utils.save(Problem, int, Path): None")
    try:
        temp_dir = Path(".", "temp").resolve()
        if not temp_dir.exists():
            os.makedirs(temp_dir)
        file_path = temp_dir / path.name
        return save(problem, iter, file_path)
    except IOError:
        Logger.warning(False, "cannot create 'temp' folder (do we have rights?)")
    return False
