from rubiks_solver.core.cube_3x3 import Cube3x3


def test_solved_cube_has_54_facelets():
    cube = Cube3x3()
    assert len(cube.facelets) == 54
    assert cube.is_solved()