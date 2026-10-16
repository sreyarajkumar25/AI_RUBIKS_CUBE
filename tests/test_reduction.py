import pytest

from rubiks_solver.core.cube_4x4 import Cube4x4
from rubiks_solver.core.cube_5x5 import Cube5x5
from rubiks_solver.reduction.as_3x3 import ReductionError, as_3x3
from rubiks_solver.reduction.reducer import Reducer


@pytest.mark.parametrize("cube_type", (Cube4x4, Cube5x5))
def test_solved_large_cube_reduces_to_solved_3x3(cube_type):
	assert as_3x3(cube_type()).is_solved()


@pytest.mark.parametrize("cube_type", (Cube4x4, Cube5x5))
def test_outer_turns_preserve_reduction_and_are_solvable(cube_type):
	cube = cube_type().apply_moves(("R", "U", "F'"))
	solution = Reducer().solve(cube, max_depth=5)
	assert cube.copy().apply_moves(solution).is_solved()


def test_unreduced_state_is_rejected():
	with pytest.raises(ReductionError):
		as_3x3(Cube4x4().apply("2R"))


@pytest.mark.parametrize("cube_type", (Cube4x4, Cube5x5))
@pytest.mark.parametrize("algorithm", ("ida_star", "bidirectional"))
def test_shallow_unreduced_scramble_uses_bounded_direct_search(cube_type, algorithm):
	cube = cube_type().apply("2R")
	solution = Reducer().solve(cube, algorithm=algorithm, max_depth=2)
	assert cube.copy().apply_moves(solution).is_solved()