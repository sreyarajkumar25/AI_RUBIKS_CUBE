"""Lehmer-code permutation ranking and unranking."""

from math import factorial


def rank_permutation(permutation: tuple[int, ...] | list[int]) -> int:
	items = list(permutation)
	if sorted(items) != list(range(len(items))):
		raise ValueError("Expected a permutation of 0..n-1")
	rank = 0
	for index, value in enumerate(items):
		smaller = sum(item < value for item in items[index + 1 :])
		rank += smaller * factorial(len(items) - index - 1)
	return rank


def unrank_permutation(rank: int, size: int) -> tuple[int, ...]:
	if size < 0 or not 0 <= rank < factorial(size):
		raise ValueError("Permutation rank is outside its valid range")
	pool = list(range(size))
	result = []
	for remaining in range(size, 0, -1):
		block = factorial(remaining - 1)
		choice, rank = divmod(rank, block)
		result.append(pool.pop(choice))
	return tuple(result)