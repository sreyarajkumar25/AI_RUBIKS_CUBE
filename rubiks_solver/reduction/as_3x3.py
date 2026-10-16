"""Validate reduction invariants and map a reduced NxN state to 3x3."""

from rubiks_solver.core.cube_3x3 import Cube3x3
from rubiks_solver.core.cube_base import CubeBase
from rubiks_solver.core.piece_model import CORNER_SLOTS, EDGE_SLOTS
from rubiks_solver.moves.move_tables import NORMALS, _facelet_geometry


class ReductionError(ValueError):
	"""Raised when centers or paired wings are not in a reducible state."""


def as_3x3(cube: CubeBase) -> Cube3x3:
	"""Collapse monochromatic centers and paired wings into a 3x3 facelet state."""
	if cube.size not in (4, 5):
		raise ValueError("Reduction conversion requires a 4x4 or 5x5 cube")
	source_geometry = _facelet_geometry(cube.size)
	target_geometry = _facelet_geometry(3)
	source_lookup = {sticker: index for index, sticker in enumerate(source_geometry)}
	target_lookup = {sticker: index for index, sticker in enumerate(target_geometry)}
	target = Cube3x3()
	maximum = cube.size - 1

	for normalized_position, faces in CORNER_SLOTS:
		source_position = tuple(value * maximum for value in normalized_position)
		target_position = tuple(value * 2 for value in normalized_position)
		for face in faces:
			normal = NORMALS[face]
			source_index = source_lookup[(source_position, normal)]
			target_index = target_lookup[(target_position, normal)]
			target.facelets[target_index] = cube.facelets[source_index]

	wing_offsets = range(-maximum + 2, maximum, 2)
	for normalized_position, faces in EDGE_SLOTS:
		axis = normalized_position.index(0)
		wing_colors = []
		for offset in wing_offsets:
			source_position = [value * maximum for value in normalized_position]
			source_position[axis] = offset
			colors = tuple(
				str(cube.facelets[source_lookup[(tuple(source_position), NORMALS[face])]])
				for face in faces
			)
			wing_colors.append(colors)
		if len(set(wing_colors)) != 1:
			raise ReductionError(f"Edge wings are not paired at {''.join(faces)}")
		target_position = tuple(value * 2 for value in normalized_position)
		for face, color in zip(faces, wing_colors[0]):
			target_index = target_lookup[(target_position, NORMALS[face])]
			target.facelets[target_index] = color

	for face in CubeBase.FACES:
		normal = NORMALS[face]
		center_indices = [
			index
			for index, (position, sticker_normal) in enumerate(source_geometry)
			if sticker_normal == normal
			and sum(abs(value) == maximum for value, direction in zip(position, normal) if direction == 0) == 0
		]
		colors = {str(cube.facelets[index]) for index in center_indices}
		if len(colors) != 1:
			raise ReductionError(f"Centers are not solved on face {face}")
		target_position = tuple(normal[axis] * 2 if normal[axis] else 0 for axis in range(3))
		target_index = target_lookup[(target_position, normal)]
		target.facelets[target_index] = colors.pop()

	return target