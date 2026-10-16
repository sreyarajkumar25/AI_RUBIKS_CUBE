"""Search statistics data structures."""

from dataclasses import dataclass


@dataclass
class SolverStats:
    nodes_expanded: int = 0
    elapsed_seconds: float = 0.0
    solution_length: int = 0