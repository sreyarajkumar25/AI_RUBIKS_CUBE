"""Facelet indexing and physical color-inventory validation helpers."""

from collections import Counter
from collections.abc import Sequence


def facelet_count(size: int) -> int:
    if size < 2:
        raise ValueError("Cube size must be at least 2")
    return 6 * size * size


def facelet_index(size: int, face_index: int, row: int, column: int) -> int:
    if not 0 <= face_index < 6 or not 0 <= row < size or not 0 <= column < size:
        raise IndexError("Facelet coordinates are outside the cube")
    return face_index * size * size + row * size + column


def validate_facelets(facelets: Sequence[str], size: int) -> bool:
    """Check facelet count and the six-color inventory for an NxN cube."""
    if size < 2 or len(facelets) != facelet_count(size):
        return False
    if any(not isinstance(color, str) or len(color) != 1 for color in facelets):
        return False
    counts = Counter(facelets)
    return len(counts) == 6 and all(count == size * size for count in counts.values())