from rubiks_solver.core.cube_3x3 import Cube3x3
from rubiks_solver.moves.move_set import get_moves


if __name__ == "__main__":
    print(f"Solved: {Cube3x3().is_solved()}")
    print(f"Available face turns: {', '.join(get_moves(3))}")