"""Combine admissible heuristics using their maximum."""

from rubiks_solver.core.cube_base import CubeBase
from rubiks_solver.heuristics.edge_manhattan import edge_manhattan


def combine_max(*values: int) -> int:
    return max(values, default=0)


def cube_heuristic(cube: CubeBase) -> int:
    """Current admissible combination; PDB terms can be added when loaded."""
    return combine_max(edge_manhattan(cube))