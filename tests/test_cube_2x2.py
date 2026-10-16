from rubiks_solver.core.cube_2x2 import Cube2x2


def test_solved_cube_has_24_facelets():
    cube = Cube2x2()
    assert len(cube.facelets) == 24
    assert cube.is_solved()