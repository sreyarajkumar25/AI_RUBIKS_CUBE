"""Front-to-front breadth-first search expanding the smaller frontier."""

from collections.abc import Callable
from math import inf
from time import monotonic

import numpy as np

from rubiks_solver.core.cube_base import CubeBase
from rubiks_solver.moves.move_set import get_moves
from rubiks_solver.moves.pruning import should_prune
from rubiks_solver.solvers.ida_star import SearchLimitExceeded
from rubiks_solver.solvers.stats import SolverStats

Heuristic = Callable[[CubeBase], int]


def _inverse(move: str) -> str:
	if move.endswith("2"):
		return move
	return move[:-1] if move.endswith("'") else move + "'"


class BidirectionalBFSSolver:
	def __init__(self, max_depth: int = 14, max_nodes: int = 2_000_000) -> None:
		self.max_depth = max_depth
		self.max_nodes = max_nodes
		self.stats = SolverStats()

	def solve(self, cube: CubeBase) -> list[str]:
		if not isinstance(cube, CubeBase):
			raise TypeError("BidirectionalBFSSolver requires a CubeBase instance")
		self.stats = SolverStats()
		if cube.is_solved():
			return []

		start_time = monotonic()
		goal = type(cube)()
		start_key = cube.state_key()
		goal_key = goal.state_key()
		forward_seen = {start_key: ()}
		backward_seen = {goal_key: ()}
		forward_frontier = {start_key: ()}
		backward_frontier = {goal_key: ()}
		forward_depth = 0
		backward_depth = 0
		best_path: tuple[str, ...] | None = None
		moves = get_moves(cube.size)

		while forward_frontier and backward_frontier:
			if best_path is not None and forward_depth + backward_depth >= len(best_path):
				break
			expand_forward = len(forward_frontier) <= len(backward_frontier)
			frontier = forward_frontier if expand_forward else backward_frontier
			own_seen = forward_seen if expand_forward else backward_seen
			other_seen = backward_seen if expand_forward else forward_seen
			next_frontier: dict[tuple[str, ...], tuple[str, ...]] = {}

			for state, path in frontier.items():
				self.stats.nodes_expanded += 1
				if self.stats.nodes_expanded > self.max_nodes:
					raise SearchLimitExceeded("Bidirectional BFS node limit exceeded")
				working = cube.copy()
				working.facelets = np.asarray(state, dtype="U1")
				previous = path[-1] if path else None
				for move in moves:
					if should_prune(previous, move):
						continue
					working.apply(move)
					next_state = working.state_key()
					next_path = path + (move,)
					if next_state not in own_seen:
						own_seen[next_state] = next_path
						next_frontier[next_state] = next_path
					opposite_path = other_seen.get(next_state)
					if opposite_path is not None:
						if expand_forward:
							candidate = next_path + tuple(_inverse(step) for step in reversed(opposite_path))
						else:
							candidate = opposite_path + tuple(_inverse(step) for step in reversed(next_path))
						if best_path is None or len(candidate) < len(best_path):
							best_path = candidate
					working.apply(_inverse(move))

			if expand_forward:
				forward_frontier = next_frontier
				forward_depth += 1
			else:
				backward_frontier = next_frontier
				backward_depth += 1
			if forward_depth + backward_depth > self.max_depth:
				break

		self.stats.elapsed_seconds = monotonic() - start_time
		if best_path is None or len(best_path) > self.max_depth:
			raise SearchLimitExceeded(f"No solution found within depth {self.max_depth}")
		self.stats.solution_length = len(best_path)
		return list(best_path)