from rubiks_solver.core.cube_4x4 import Cube4x4


def test_solved_cube_has_96_facelets():
    cube = Cube4x4()
    assert len(cube.facelets) == 96
    assert cube.is_solved()