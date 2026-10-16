from rubiks_solver.core.cube_2x2 import Cube2x2
from rubiks_solver.core.cube_3x3 import Cube3x3
from rubiks_solver.heuristics.edge_manhattan import edge_manhattan


def test_piece_coordinate_extraction_and_heuristic_on_solved_states():
	assert edge_manhattan(Cube2x2()) == 0
	assert edge_manhattan(Cube3x3()) == 0


def test_heuristic_is_bounded_by_known_scramble_lengths():
	for cube_type in (Cube2x2, Cube3x3):
		for scramble in (("R",), ("R", "U"), ("R", "U", "F")):
			cube = cube_type().apply_moves(scramble)
			assert edge_manhattan(cube) <= len(scramble)