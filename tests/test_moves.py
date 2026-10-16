import unittest

from rubiks_solver.core.cube_2x2 import Cube2x2
from rubiks_solver.core.cube_3x3 import Cube3x3
from rubiks_solver.core.cube_4x4 import Cube4x4
from rubiks_solver.core.cube_5x5 import Cube5x5
from rubiks_solver.core.facelet_utils import validate_facelets
from rubiks_solver.moves.move_set import get_moves


def test_wide_turns_are_only_available_for_large_cubes():
    assert "Rw" not in get_moves(3)
    assert "Rw" in get_moves(4)


class MovePermutationTests(unittest.TestCase):
    def test_facelet_counts_and_move_periodicity(self):
        for cube_type, size in ((Cube2x2, 2), (Cube3x3, 3), (Cube4x4, 4), (Cube5x5, 5)):
            solved = cube_type()
            self.assertEqual(len(solved.facelets), 6 * size * size)
            for move in get_moves(size):
                cube = solved.copy()
                for _ in range(4):
                    cube.apply(move)
                self.assertEqual(cube.state_key(), solved.state_key(), (size, move))

    def test_move_inverse_cancellation(self):
        for size in range(2, 6):
            cube_type = (Cube2x2, Cube3x3, Cube4x4, Cube5x5)[size - 2]
            solved = cube_type()
            for move in get_moves(size):
                inverse = move if move.endswith("2") else move[:-1] if move.endswith("'") else move + "'"
                moved = solved.copy().apply(move).apply(inverse)
                self.assertEqual(moved.state_key(), solved.state_key(), (size, move))

    def test_facelet_inventory_validation(self):
        cube = Cube3x3()
        self.assertTrue(validate_facelets(cube.facelets, 3))
        invalid = cube.facelets.copy()
        invalid[0] = "R"
        self.assertFalse(validate_facelets(invalid, 3))
        with self.assertRaises(ValueError):
            Cube3x3.from_facelets(invalid)