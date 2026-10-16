"""Piece abstractions and coordinate extraction from facelet states."""

from dataclasses import dataclass

from rubiks_solver.core.cube_base import CubeBase
from rubiks_solver.moves.move_tables import _facelet_geometry

CORNER_SLOTS = (
    ((1, 1, 1), ("U", "R", "F")),
    ((-1, 1, 1), ("U", "F", "L")),
    ((-1, 1, -1), ("U", "L", "B")),
    ((1, 1, -1), ("U", "B", "R")),
    ((1, -1, 1), ("D", "F", "R")),
    ((-1, -1, 1), ("D", "L", "F")),
    ((-1, -1, -1), ("D", "B", "L")),
    ((1, -1, -1), ("D", "R", "B")),
)
EDGE_SLOTS = (
    ((1, 1, 0), ("U", "R")),
    ((0, 1, 1), ("U", "F")),
    ((-1, 1, 0), ("U", "L")),
    ((0, 1, -1), ("U", "B")),
    ((1, -1, 0), ("D", "R")),
    ((0, -1, 1), ("D", "F")),
    ((-1, -1, 0), ("D", "L")),
    ((0, -1, -1), ("D", "B")),
    ((1, 0, 1), ("F", "R")),
    ((-1, 0, 1), ("F", "L")),
    ((-1, 0, -1), ("B", "L")),
    ((1, 0, -1), ("B", "R")),
)


@dataclass(frozen=True)
class Piece:
    kind: str
    stickers: tuple[str, ...]
    position: int
    orientation: int = 0


def _facelet_lookup(cube: CubeBase) -> dict[tuple[tuple[int, int, int], tuple[int, int, int]], int]:
    return {sticker: index for index, sticker in enumerate(_facelet_geometry(cube.size))}


def extract_corner_state(
    cube: CubeBase, validate: bool = True
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return corner permutation and twist coordinates for a 2x2-5x5 state."""
    scale = cube.size - 1
    lookup = _facelet_lookup(cube)
    solved_pieces = [tuple(faces) for _, faces in CORNER_SLOTS]
    piece_by_colors = {frozenset(piece): index for index, piece in enumerate(solved_pieces)}
    permutation = []
    orientation = []
    for position, faces in CORNER_SLOTS:
        scaled_position = tuple(value * scale for value in position)
        current = tuple(
            str(cube.facelets[lookup[(scaled_position, _normal(face))]])
            for face in faces
        )
        piece_index = piece_by_colors.get(frozenset(current))
        if piece_index is None:
            raise ValueError("Facelets do not describe a valid corner piece")
        solved = solved_pieces[piece_index]
        twist = next(
            (offset for offset in range(3) if current == solved[offset:] + solved[:offset]),
            None,
        )
        if twist is None:
            raise ValueError("Corner stickers have an invalid orientation")
        permutation.append(piece_index)
        orientation.append(twist)
    if validate and sum(orientation) % 3:
        raise ValueError("Corner twist sum is invalid")
    return tuple(permutation), tuple(orientation)


def extract_edge_state(
    cube: CubeBase, validate: bool = True
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return 3x3 edge permutation and flip coordinates."""
    if cube.size != 3:
        raise ValueError("Edge coordinates are defined for a 3x3 state")
    lookup = _facelet_lookup(cube)
    solved_pieces = [tuple(faces) for _, faces in EDGE_SLOTS]
    piece_by_colors = {frozenset(piece): index for index, piece in enumerate(solved_pieces)}
    permutation = []
    orientation = []
    for position, faces in EDGE_SLOTS:
        scaled_position = tuple(value * (cube.size - 1) for value in position)
        current = tuple(
            str(cube.facelets[lookup[(scaled_position, _normal(face))]])
            for face in faces
        )
        piece_index = piece_by_colors.get(frozenset(current))
        if piece_index is None:
            raise ValueError("Facelets do not describe a valid edge piece")
        solved = solved_pieces[piece_index]
        if current == solved:
            flip = 0
        elif current == solved[::-1]:
            flip = 1
        else:
            raise ValueError("Edge stickers have an invalid orientation")
        permutation.append(piece_index)
        orientation.append(flip)
    if validate and sum(orientation) % 2:
        raise ValueError("Edge flip sum is invalid")
    return tuple(permutation), tuple(orientation)


def _normal(face: str) -> tuple[int, int, int]:
    return {
        "U": (0, 1, 0),
        "R": (1, 0, 0),
        "F": (0, 0, 1),
        "D": (0, -1, 0),
        "L": (-1, 0, 0),
        "B": (0, 0, -1),
    }[face]