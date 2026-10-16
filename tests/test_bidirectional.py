from rubiks_solver.core.cube_3x3 import Cube3x3
from rubiks_solver.solvers.bidirectional_bfs import BidirectionalBFSSolver


def test_bidirectional_bfs_finds_optimal_two_move_solution():
	cube = Cube3x3().apply_moves(("R", "U"))
	solution = BidirectionalBFSSolver(max_depth=4).solve(cube)
	assert len(solution) == 2
	assert cube.copy().apply_moves(solution).is_solved()