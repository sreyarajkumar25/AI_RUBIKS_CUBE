"""Iterative Deepening A* with transposition and move pruning."""

from collections.abc import Callable
from math import inf
from time import monotonic

from rubiks_solver.core.cube_base import CubeBase
from rubiks_solver.moves.move_set import get_moves
from rubiks_solver.moves.pruning import face_of, should_prune
from rubiks_solver.solvers.stats import SolverStats

Heuristic = Callable[[CubeBase], int]


class SearchLimitExceeded(RuntimeError):
	"""Raised when a configured search resource limit is reached."""


def _zero_heuristic(cube: CubeBase) -> int:
	return 0


class IDAStarSolver:
	def __init__(
		self,
		heuristic: Heuristic = _zero_heuristic,
		max_depth: int = 30,
		max_nodes: int | None = 2_000_000,
	) -> None:
		self.heuristic = heuristic
		self.max_depth = max_depth
		self.max_nodes = max_nodes
		self.stats = SolverStats()

	def solve(self, cube: CubeBase) -> list[str]:
		if not isinstance(cube, CubeBase):
			raise TypeError("IDAStarSolver requires a CubeBase instance")
		self.stats = SolverStats()
		if cube.is_solved():
			return []

		working = cube.copy()
		moves = get_moves(cube.size)
		path: list[str] = []
		threshold = self.heuristic(working)
		start_time = monotonic()

		def search(
			depth: int,
			bound: int,
			previous: str | None,
			table: dict[tuple[tuple[str, ...], str | None], int],
		) -> int | bool:
			self.stats.nodes_expanded += 1
			if self.max_nodes is not None and self.stats.nodes_expanded > self.max_nodes:
				raise SearchLimitExceeded("IDA* node limit exceeded")
			score = depth + self.heuristic(working)
			if score > bound:
				return score
			if working.is_solved():
				return True
			key = (working.state_key(), face_of(previous) if previous else None)
			if table.get(key, depth + 1) <= depth:
				return inf
			table[key] = depth
			minimum = inf
			for move in moves:
				if should_prune(previous, move):
					continue
				working.apply(move)
				path.append(move)
				result = search(depth + 1, bound, move, table)
				if result is True:
					return True
				path.pop()
				inverse = move if move.endswith("2") else move[:-1] if move.endswith("'") else move + "'"
				working.apply(inverse)
				minimum = min(minimum, result)
			return minimum

		while threshold <= self.max_depth:
			result = search(0, threshold, None, {})
			if result is True:
				self.stats.solution_length = len(path)
				self.stats.elapsed_seconds = monotonic() - start_time
				return path.copy()
			if result == inf:
				break
			threshold = int(result)
		self.stats.elapsed_seconds = monotonic() - start_time
		raise SearchLimitExceeded(f"No solution found within depth {self.max_depth}")