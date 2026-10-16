from rubiks_solver.core.cube_3x3 import Cube3x3


if __name__ == "__main__":
    cube = Cube3x3()
    print(f"Solved: {cube.is_solved()}")