"""Generate and cache geometric facelet permutations by cube size."""

from functools import lru_cache
import re

import numpy as np


FACES = ("U", "R", "F", "D", "L", "B")
NORMALS = {
	"U": (0, 1, 0),
	"R": (1, 0, 0),
	"F": (0, 0, 1),
	"D": (0, -1, 0),
	"L": (-1, 0, 0),
	"B": (0, 0, -1),
}
MOVE_PATTERN = re.compile(r"(?:(\d+))?([URFDLB])(w)?(2|')?\Z")


def _facelet_geometry(size: int) -> list[tuple[tuple[int, int, int], tuple[int, int, int]]]:
	maximum = size - 1
	coordinates = range(-maximum, maximum + 1, 2)
	geometry = []
	for face in FACES:
		for row in range(size):
			for column in range(size):
				horizontal = -maximum + 2 * column
				vertical = maximum - 2 * row
				if face == "U":
					position = (horizontal, maximum, -maximum + 2 * row)
				elif face == "R":
					position = (maximum, vertical, maximum - 2 * column)
				elif face == "F":
					position = (horizontal, vertical, maximum)
				elif face == "D":
					position = (horizontal, -maximum, maximum - 2 * row)
				elif face == "L":
					position = (-maximum, vertical, -maximum + 2 * column)
				else:
					position = (maximum - 2 * column, vertical, -maximum)
				geometry.append((position, NORMALS[face]))
	if len(coordinates) != size:
		raise AssertionError("Coordinate generation failed")
	return geometry


def _rotate_clockwise(
	vector: tuple[int, int, int], axis: tuple[int, int, int]
) -> tuple[int, int, int]:
	dot = sum(value * direction for value, direction in zip(vector, axis))
	cross = (
		axis[1] * vector[2] - axis[2] * vector[1],
		axis[2] * vector[0] - axis[0] * vector[2],
		axis[0] * vector[1] - axis[1] * vector[0],
	)
	return tuple(dot * axis[index] - cross[index] for index in range(3))


def _parse_move(size: int, move: str) -> tuple[str, set[int], int]:
	match = MOVE_PATTERN.fullmatch(move)
	if match is None:
		raise ValueError(f"Invalid move notation: {move}")
	layer_text, face, wide_text, suffix = match.groups()
	maximum = size - 1
	if wide_text:
		width = int(layer_text) if layer_text else 2
		if width < 2 or width > size:
			raise ValueError(f"Wide move is invalid for a {size}x{size} cube: {move}")
		offsets = range(width)
	elif layer_text:
		offset = int(layer_text) - 1
		if offset < 1 or offset >= size:
			raise ValueError(f"Inner slice is invalid for a {size}x{size} cube: {move}")
		offsets = (offset,)
	else:
		offsets = (0,)
	layers = {maximum - 2 * offset for offset in offsets}
	turns = {None: 1, "'": 3, "2": 2}[suffix]
	return face, layers, turns


@lru_cache(maxsize=None)
def _quarter_turn(size: int, face: str, layers: frozenset[int]) -> np.ndarray:
	geometry = _facelet_geometry(size)
	indices = {sticker: index for index, sticker in enumerate(geometry)}
	axis = NORMALS[face]
	permutation = np.arange(len(geometry), dtype=np.int32)
	for source, (position, normal) in enumerate(geometry):
		depth = sum(value * direction for value, direction in zip(position, axis))
		if depth not in layers:
			continue
		rotated_position = _rotate_clockwise(position, axis)
		rotated_normal = _rotate_clockwise(normal, axis)
		destination = indices[(rotated_position, rotated_normal)]
		permutation[destination] = source
	permutation.flags.writeable = False
	return permutation


@lru_cache(maxsize=None)
def get_move_permutation(size: int, move: str) -> np.ndarray:
	"""Return the cached source-index permutation for a move token."""
	if size < 2:
		raise ValueError("Cube size must be at least 2")
	face, layers, turns = _parse_move(size, move)
	quarter = _quarter_turn(size, face, frozenset(layers))
	permutation = quarter
	for _ in range(turns - 1):
		permutation = permutation[quarter]
	permutation.flags.writeable = False
	return permutation