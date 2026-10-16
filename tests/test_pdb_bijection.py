from rubiks_solver.heuristics.corner_pdb import rank_corner_state
from rubiks_solver.heuristics.edge_orientation_pdb import rank_edge_orientation
from rubiks_solver.utils.factoradic import rank_permutation, unrank_permutation
from rubiks_solver.utils.ternary_rank import rank_orientation, unrank_orientation
from rubiks_solver.utils.bitpacking import pack_nibbles, unpack_nibbles


def test_permutation_rank_roundtrip():
	for permutation in ((0, 1, 2, 3), (2, 0, 3, 1), (7, 6, 5, 4, 3, 2, 1, 0)):
		assert unrank_permutation(rank_permutation(permutation), len(permutation)) == permutation


def test_corner_and_edge_orientation_ranks_cover_valid_ranges():
	orientations = unrank_orientation(1234, 8)
	rank = rank_corner_state((0, 1, 2, 3, 4, 5, 6, 7), orientations)
	assert 0 <= rank < 88_179_840
	assert rank_edge_orientation((0,) * 12) == 0


def test_orientation_rank_roundtrip():
	for rank in (0, 1, 100, 2186):
		assert rank_orientation(unrank_orientation(rank, 8)) == rank


def test_nibble_packing_roundtrip_with_odd_length():
	values = (0, 1, 15, 8, 3)
	packed = pack_nibbles(values)
	assert len(packed) == 3
	assert tuple(unpack_nibbles(packed, len(values))) == values