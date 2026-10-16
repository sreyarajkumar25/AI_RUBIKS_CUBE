"""Argument parser for package commands."""

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rubiks-solver")
    commands = parser.add_subparsers(dest="command")

    solve_parser = commands.add_parser("solve", help="solve a cube scramble")
    solve_parser.add_argument("--scramble", required=True)
    solve_parser.add_argument("--size", type=int, choices=range(2, 6), default=3)
    solve_parser.add_argument(
        "--algo", "--algorithm", choices=("ida_star", "bidirectional"), default="ida_star"
    )
    solve_parser.add_argument("--visualize", action="store_true")

    scramble_parser = commands.add_parser("scramble", help="generate a random scramble")
    scramble_parser.add_argument("--size", type=int, choices=range(2, 6), default=3)
    scramble_parser.add_argument("--moves", type=int, default=25)

    benchmark_parser = commands.add_parser("benchmark", help="benchmark solver engines")
    benchmark_parser.add_argument("--size", type=int, choices=range(2, 6), default=3)
    benchmark_parser.add_argument("--trials", type=int, default=100)
    benchmark_parser.add_argument("--algo", choices=("ida_star", "bidirectional"), default="ida_star")

    pdb_parser = commands.add_parser("generate-pdb", help="generate a pattern database")
    pdb_parser.add_argument("--type", choices=("corner", "edge-orientation", "center"), required=True)
    pdb_parser.add_argument("--depth", type=int, required=True)
    pdb_parser.add_argument("--out", required=True)
    return parser