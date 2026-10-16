from rubiks_solver.core.cube_5x5 import Cube5x5


def test_solved_cube_has_150_facelets():
    cube = Cube5x5()
    assert len(cube.facelets) == 150
    assert cube.is_solved()