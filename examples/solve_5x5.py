from rubiks_solver.core.cube_5x5 import Cube5x5


if __name__ == "__main__":
    cube = Cube5x5()
    print(f"Solved: {cube.is_solved()}")