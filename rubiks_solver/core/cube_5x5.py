"""5x5 cube model with wings and center pieces."""

from rubiks_solver.core.cube_base import CubeBase


class Cube5x5(CubeBase):
    @classmethod
    def cube_size(cls) -> int:
        return 5