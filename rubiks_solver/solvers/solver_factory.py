"""Solver selection and shared solver facade."""

from rubiks_solver.solvers.bidirectional_bfs import BidirectionalBFSSolver
from rubiks_solver.solvers.ida_star import IDAStarSolver
from rubiks_solver.heuristics.max_combination import cube_heuristic


class Solver:
    def __init__(self, algorithm: str = "ida_star", **options: object) -> None:
        self.algorithm = algorithm
        self.engine = create_solver(algorithm, **options)

    def solve(self, cube: object) -> list[str]:
        return self.engine.solve(cube)


def create_solver(algorithm: str = "ida_star", **options: object) -> IDAStarSolver | BidirectionalBFSSolver:
    if algorithm == "ida_star":
        options.setdefault("heuristic", cube_heuristic)
        return IDAStarSolver(**options)
    if algorithm in {"bidirectional", "bidirectional_bfs"}:
        return BidirectionalBFSSolver(**options)
    raise ValueError(f"Unknown solver algorithm: {algorithm}")