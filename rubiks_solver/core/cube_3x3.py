"""3x3 cube model."""

from rubiks_solver.core.cube_base import CubeBase


class Cube3x3(CubeBase):
    @classmethod
    def cube_size(cls) -> int:
        return 3