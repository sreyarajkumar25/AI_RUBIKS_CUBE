from rubiks_solver.core.cube_3x3 import Cube3x3
from rubiks_solver.moves.scramble import generate_scramble
from rubiks_solver.solvers.solver_factory import Solver
from rubiks_solver.visualizer.nxn_visualizer import Visualizer


if __name__ == "__main__":
    scramble = generate_scramble(3, 5)
    cube = Cube3x3().apply_moves(scramble)
    solution = Solver("ida_star", max_depth=12, max_nodes=300_000).solve(cube.copy())
    print("Scramble:", " ".join(scramble))
    print("Solution:", " ".join(solution))
    Visualizer().render(cube, solution)