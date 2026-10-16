"""Canonical search pruning for same-face and opposite-face turns."""

import re


MOVE_FACE = re.compile(r"\d*([URFDLB])")
OPPOSITE = {"U": "D", "D": "U", "R": "L", "L": "R", "F": "B", "B": "F"}
FACE_ORDER = {"U": 0, "D": 1, "R": 2, "L": 3, "F": 4, "B": 5}


def face_of(move: str) -> str:
	match = MOVE_FACE.match(move)
	if match is None:
		raise ValueError(f"Invalid move token: {move}")
	return match.group(1)


def should_prune(previous_move: str | None, move: str) -> bool:
	if previous_move is None:
		return False
	previous_face = face_of(previous_move)
	current_face = face_of(move)
	if previous_face == current_face:
		return True
	return (
		OPPOSITE[previous_face] == current_face
		and FACE_ORDER[previous_face] > FACE_ORDER[current_face]
	)