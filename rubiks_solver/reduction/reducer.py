"""Reduce already paired 4x4/5x5 cubes and solve the resulting 3x3 state."""

from rubiks_solver.core.cube_base import CubeBase
from rubiks_solver.reduction.as_3x3 import ReductionError, as_3x3
from rubiks_solver.reduction.parity_detector import detect_parity
from rubiks_solver.solvers.solver_factory import Solver


class Reducer:
    def reduce(self, cube: CubeBase) -> CubeBase:
        """Convert a fully reduced 4x4/5x5 state to its 3x3 representation."""
        if cube.size == 3:
            return cube.copy()
        if cube.size not in (4, 5):
            raise ValueError("Reduction is only defined for 4x4 and 5x5 cubes")
        reduced = as_3x3(cube)
        report = detect_parity(reduced)
        if not report.is_legal_3x3_state:
            raise ReductionError(
                "Reduced state has OLL/PLL parity; parity correction algorithms "
                "are not yet implemented"
            )
        return reduced

    def solve(
        self, cube: CubeBase, algorithm: str = "ida_star", **options: object
    ) -> list[str]:
        """Solve a 2x2/3x3 state or a bounded/reduced larger-cube state."""
        if cube.size == 2:
            reduced = cube.copy()
        else:
            try:
                reduced = self.reduce(cube)
            except ReductionError:
                if cube.size < 4:
                    raise
                return Solver(algorithm, **options).solve(cube)
        return Solver(algorithm, **options).solve(reduced)