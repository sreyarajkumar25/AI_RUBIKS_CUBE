"""Apply precomputed NumPy facelet permutations."""

import numpy as np


def apply_permutation(
    facelets: np.ndarray, permutation: np.ndarray
) -> np.ndarray:
    if len(facelets) != len(permutation):
        raise ValueError("Permutation length must match facelet count")
    return facelets[permutation]