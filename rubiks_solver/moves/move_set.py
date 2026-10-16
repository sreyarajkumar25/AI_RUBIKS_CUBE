"""Move notation supported by each cube size."""


def get_moves(size: int) -> list[str]:
    if size < 2:
        raise ValueError("Cube size must be at least 2")
    faces = ("U", "R", "F", "D", "L", "B")
    suffixes = ("", "'", "2")
    moves = [face + suffix for face in faces for suffix in suffixes]
    if size >= 4:
        moves.extend(
            face + "w" + suffix for face in faces for suffix in suffixes
        )
        moves.extend(
            f"{layer}{face}{suffix}"
            for layer in range(2, size)
            for face in faces
            for suffix in suffixes
        )
    return moves