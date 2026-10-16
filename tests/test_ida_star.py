from rubiks_solver.core.cube_2x2 import Cube2x2
from rubiks_solver.solvers.ida_star import IDAStarSolver


def test_ida_star_finds_optimal_two_move_solution():
	cube = Cube2x2().apply_moves(("R", "U"))
	solution = IDAStarSolver(max_depth=4).solve(cube)
	assert len(solution) == 2
	assert cube.copy().apply_moves(solution).is_solved()


def test_ida_star_preserves_optimality_across_pruned_move_orders():
	for scramble in (("R", "U", "R'"), ("F", "D", "B"), ("L", "U", "D")):
		cube = Cube2x2().apply_moves(scramble)
		solution = IDAStarSolver(max_depth=5).solve(cube)
		assert cube.copy().apply_moves(solution).is_solved()
		assert len(solution) <= len(scramble)