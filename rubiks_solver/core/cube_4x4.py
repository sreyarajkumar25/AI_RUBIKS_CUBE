"""4x4 cube model with wings and movable centers."""

from rubiks_solver.core.cube_base import CubeBase


class Cube4x4(CubeBase):
    @classmethod
    def cube_size(cls) -> int:
        return 4