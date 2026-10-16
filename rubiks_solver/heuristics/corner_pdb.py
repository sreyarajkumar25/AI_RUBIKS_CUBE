"""Corner coordinate ranking and pattern database lookup."""

from pathlib import Path

from rubiks_solver.utils.factoradic import rank_permutation
from rubiks_solver.utils.ternary_rank import rank_orientation
from rubiks_solver.heuristics.pdb_io import load_pdb

CORNER_PERMUTATIONS = 40_320
CORNER_ORIENTATIONS = 2_187
CORNER_STATE_COUNT = CORNER_PERMUTATIONS * CORNER_ORIENTATIONS


def rank_corner_state(permutation: tuple[int, ...], orientation: tuple[int, ...]) -> int:
	if len(permutation) != 8 or len(orientation) != 8:
		raise ValueError("Corner state must contain eight pieces")
	return rank_permutation(permutation) * CORNER_ORIENTATIONS + rank_orientation(orientation)


class CornerPatternDatabase:
	def __init__(self, path: str | Path) -> None:
		self.values = load_pdb(path, CORNER_STATE_COUNT)

	def lookup(self, permutation: tuple[int, ...], orientation: tuple[int, ...]) -> int:
		return int(self.values[rank_corner_state(permutation, orientation)])