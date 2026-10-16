"""2x2 cube model (corners only)."""

from rubiks_solver.core.cube_base import CubeBase


class Cube2x2(CubeBase):
    @classmethod
    def cube_size(cls) -> int:
        return 2