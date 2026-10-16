"""Rank and unrank twist orientations with a fixed orientation sum."""


def rank_orientation(orientations: tuple[int, ...] | list[int], radix: int = 3) -> int:
	if not orientations or radix < 2 or any(not 0 <= value < radix for value in orientations):
		raise ValueError("Invalid orientation vector")
	if sum(orientations) % radix:
		raise ValueError("Orientation sum violates the cube constraint")
	rank = 0
	for value in orientations[:-1]:
		rank = rank * radix + value
	return rank


def unrank_orientation(rank: int, count: int, radix: int = 3) -> tuple[int, ...]:
	state_count = radix ** (count - 1)
	if count < 1 or not 0 <= rank < state_count:
		raise ValueError("Orientation rank is outside its valid range")
	result = [0] * count
	for index in range(count - 2, -1, -1):
		rank, result[index] = divmod(rank, radix)
	result[-1] = (-sum(result[:-1])) % radix
	return tuple(result)