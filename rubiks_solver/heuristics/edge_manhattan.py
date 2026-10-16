"""Admissible displaced-piece lower bound for direct 2x2/3x3 search."""

from math import ceil

from rubiks_solver.core.cube_base import CubeBase
from rubiks_solver.core.piece_model import extract_corner_state, extract_edge_state


def edge_manhattan(cube: CubeBase) -> int:
	"""Bound turns by the maximum number of pieces one move can displace."""
	corner_permutation, corner_orientation = extract_corner_state(cube)
	corner_misplaced = sum(index != piece for index, piece in enumerate(corner_permutation))
	corner_twisted = sum(value != 0 for value in corner_orientation)
	bounds = [ceil(corner_misplaced / 4), ceil(corner_twisted / 4)]
	if cube.size == 3:
		edge_permutation, edge_orientation = extract_edge_state(cube)
		edge_misplaced = sum(index != piece for index, piece in enumerate(edge_permutation))
		edge_flipped = sum(value != 0 for value in edge_orientation)
		bounds.extend((ceil(edge_misplaced / 4), ceil(edge_flipped / 4)))
	return max(bounds)