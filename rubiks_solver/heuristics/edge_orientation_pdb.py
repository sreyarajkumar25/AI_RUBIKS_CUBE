"""Rank edge orientation states and access the 2,048-state table."""

from pathlib import Path

from rubiks_solver.heuristics.pdb_io import load_pdb


def rank_edge_orientation(orientation: tuple[int, ...] | list[int]) -> int:
	if len(orientation) != 12 or any(value not in (0, 1) for value in orientation):
		raise ValueError("Edge orientation must contain twelve binary values")
	if sum(orientation) % 2:
		raise ValueError("Edge orientation parity is invalid")
	rank = 0
	for value in orientation[:-1]:
		rank = (rank << 1) | value
	return rank


class EdgeOrientationDatabase:
	def __init__(self, path: str | Path) -> None:
		self.values = load_pdb(path, 2_048)

	def lookup(self, orientation: tuple[int, ...] | list[int]) -> int:
		return int(self.values[rank_edge_orientation(orientation)])