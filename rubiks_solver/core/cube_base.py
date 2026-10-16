"""Shared facelet representation and behavior for NxN cube models."""

from abc import ABC, abstractmethod
from collections.abc import Iterable

import numpy as np

from rubiks_solver.moves.move_tables import get_move_permutation
from rubiks_solver.core.facelet_utils import validate_facelets


class CubeBase(ABC):
    """Abstract cube interface using six contiguous facelet regions."""

    FACES = ("U", "R", "F", "D", "L", "B")

    @classmethod
    @abstractmethod
    def cube_size(cls) -> int:
        """Return this cube model's edge length."""

    def __init__(self) -> None:
        self.size = self.cube_size()
        self.facelets = np.repeat(np.asarray(self.FACES, dtype="U1"), self.size**2)

    @property
    def facelet_count(self) -> int:
        return 6 * self.size * self.size

    @classmethod
    def from_facelets(cls, facelets: Iterable[str]) -> CubeBase:
        """Create a cube from a validated sequence of six equally sized colors."""
        values = list(facelets)
        cube = cls()
        if not validate_facelets(values, cube.size):
            raise ValueError(f"Expected a physically balanced {cube.size}x{cube.size} facelet inventory")
        cube.facelets = np.asarray(values, dtype="U1")
        return cube

    def state_key(self) -> tuple[str, ...]:
        return tuple(self.facelets.tolist())

    def is_solved(self) -> bool:
        faces = self.facelets.reshape(6, self.size * self.size)
        return bool(np.all(faces == faces[:, :1]))

    def apply(self, move: str) -> CubeBase:
        """Apply one move using its cached facelet permutation."""
        self.facelets = self.facelets[get_move_permutation(self.size, move)]
        return self

    def apply_moves(self, moves: Iterable[str]) -> CubeBase:
        for move in moves:
            self.apply(move)
        return self

    def copy(self) -> CubeBase:
        duplicate = type(self)()
        duplicate.facelets = self.facelets.copy()
        return duplicate