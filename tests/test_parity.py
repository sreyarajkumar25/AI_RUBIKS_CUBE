from rubiks_solver.core.cube_3x3 import Cube3x3
from rubiks_solver.reduction.parity_detector import detect_parity


def test_legal_outer_moves_have_no_reduction_parity():
	for scramble in (("R",), ("U", "F", "R'"), ("L2", "D", "B2")):
		report = detect_parity(Cube3x3().apply_moves(scramble))
		assert report.is_legal_3x3_state