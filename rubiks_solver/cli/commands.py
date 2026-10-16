"""Working CLI commands for cube models and search engines."""

import argparse
import random
import statistics
import time

from rubiks_solver.core.cube_2x2 import Cube2x2
from rubiks_solver.core.cube_3x3 import Cube3x3
from rubiks_solver.core.cube_4x4 import Cube4x4
from rubiks_solver.core.cube_5x5 import Cube5x5
from rubiks_solver.cli.arg_parser import build_parser
from rubiks_solver.moves.move_set import get_moves
from rubiks_solver.moves.pruning import should_prune
from rubiks_solver.reduction.reducer import Reducer
from rubiks_solver.solvers.ida_star import SearchLimitExceeded
from rubiks_solver.solvers.solver_factory import Solver

CUBE_TYPES = {2: Cube2x2, 3: Cube3x3, 4: Cube4x4, 5: Cube5x5}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        if args.command == "solve":
            return _solve(args, parser)
        if args.command == "scramble":
            return _scramble(args)
        if args.command == "benchmark":
            return _benchmark(args, parser)
        if args.command == "generate-pdb":
            parser.error("pattern database generation is not implemented yet")
    except (SearchLimitExceeded, ValueError) as error:
        parser.error(str(error))
    return 0


def _solve(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    cube = CUBE_TYPES[args.size]()
    scramble = args.scramble.split()
    cube.apply_moves(scramble)
    initial = cube.copy()
    if args.size >= 4:
        solution = Reducer().solve(cube, args.algo)
    else:
        solver = Solver(args.algo)
        solution = solver.solve(cube)
    print("Solution:", " ".join(solution) if solution else "(already solved)")
    if args.visualize:
        from rubiks_solver.visualizer.nxn_visualizer import Visualizer

        Visualizer().render(initial, solution)
    return 0


def _scramble(args: argparse.Namespace) -> int:
    if args.moves < 0:
        raise ValueError("--moves must be non-negative")
    choices = get_moves(args.size)
    sequence: list[str] = []
    while len(sequence) < args.moves:
        move = random.choice(choices)
        if not should_prune(sequence[-1] if sequence else None, move):
            sequence.append(move)
    print(" ".join(sequence))
    return 0


def _benchmark(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.trials < 1:
        raise ValueError("--trials must be positive")
    if args.size >= 4:
        parser.error("benchmarking 4x4/5x5 requires the unfinished reduction pipeline")
    times = []
    lengths = []
    for _ in range(args.trials):
        scramble = _scramble_tokens(args.size, 4)
        cube = CUBE_TYPES[args.size]().apply_moves(scramble)
        solver = Solver(args.algo)
        started = time.perf_counter()
        solution = solver.solve(cube)
        times.append(time.perf_counter() - started)
        lengths.append(len(solution))
    print(f"Trials: {args.trials}")
    print(f"Mean solve time: {statistics.mean(times):.6f}s")
    print(f"Mean solution length: {statistics.mean(lengths):.2f}")
    return 0


def _scramble_tokens(size: int, count: int) -> list[str]:
    choices = get_moves(size)
    result: list[str] = []
    while len(result) < count:
        move = random.choice(choices)
        if not should_prune(result[-1] if result else None, move):
            result.append(move)
    return result