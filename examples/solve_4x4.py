from rubiks_solver.core.cube_4x4 import Cube4x4


if __name__ == "__main__":
    cube = Cube4x4()
    print(f"Solved: {cube.is_solved()}")