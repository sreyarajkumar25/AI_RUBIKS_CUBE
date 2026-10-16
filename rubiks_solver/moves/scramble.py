"""Generate random move sequences without trivially canceling adjacent turns."""

import random

from rubiks_solver.moves.move_set import get_moves
from rubiks_solver.moves.pruning import should_prune


def generate_scramble(size: int, length: int, seed: int | None = None) -> list[str]:
    if length < 0:
        raise ValueError("Scramble length must be non-negative")
    rng = random.Random(seed)
    choices = get_moves(size)
    scramble: list[str] = []
    while len(scramble) < length:
        move = rng.choice(choices)
        if not should_prune(scramble[-1] if scramble else None, move):
            scramble.append(move)
    return scramble