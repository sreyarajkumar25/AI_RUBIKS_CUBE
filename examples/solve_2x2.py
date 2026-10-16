from rubiks_solver.core.cube_2x2 import Cube2x2


if __name__ == "__main__":
    cube = Cube2x2()
    print(f"Solved: {cube.is_solved()}")