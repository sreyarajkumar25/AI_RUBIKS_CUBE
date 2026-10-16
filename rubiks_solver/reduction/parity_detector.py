"""Report permutation and orientation parity in reduced 3x3 states."""

from dataclasses import dataclass

from rubiks_solver.core.cube_base import CubeBase
from rubiks_solver.core.piece_model import extract_corner_state, extract_edge_state


@dataclass(frozen=True)
class ParityReport:
	corner_twist_sum: int
	edge_flip_sum: int
	corner_permutation_parity: int
	edge_permutation_parity: int

	@property
	def oll_parity(self) -> bool:
		return self.edge_flip_sum % 2 != 0

	@property
	def pll_parity(self) -> bool:
		return self.corner_permutation_parity != self.edge_permutation_parity

	@property
	def is_legal_3x3_state(self) -> bool:
		return not self.oll_parity and not self.pll_parity and self.corner_twist_sum % 3 == 0


def _permutation_parity(permutation: tuple[int, ...]) -> int:
	inversions = sum(
		left > right
		for index, left in enumerate(permutation)
		for right in permutation[index + 1 :]
	)
	return inversions % 2


def detect_parity(cube: CubeBase) -> ParityReport:
	"""Inspect a 3x3 cube or a reduced state without discarding parity signals."""
	if cube.size != 3:
		raise ValueError("Parity detection requires a 3x3 representation")
	corners, twists = extract_corner_state(cube, validate=False)
	edges, flips = extract_edge_state(cube, validate=False)
	return ParityReport(
		corner_twist_sum=sum(twists),
		edge_flip_sum=sum(flips),
		corner_permutation_parity=_permutation_parity(corners),
		edge_permutation_parity=_permutation_parity(edges),
	)