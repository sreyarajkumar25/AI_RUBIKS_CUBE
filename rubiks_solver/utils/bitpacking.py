"""Pack and unpack 4-bit pattern database distances."""

from collections.abc import Sequence

import numpy as np


def pack_nibbles(values: Sequence[int] | np.ndarray) -> np.ndarray:
	"""Pack two unsigned 4-bit values into each byte, low nibble first."""
	unpacked = np.asarray(values, dtype=np.int64).reshape(-1)
	if np.any(unpacked < 0) or np.any(unpacked > 15):
		raise ValueError("Nibble values must be between 0 and 15")
	packed = np.zeros((unpacked.size + 1) // 2, dtype=np.uint8)
	packed[:] = unpacked[::2].astype(np.uint8)
	if unpacked.size > 1:
		pair_count = unpacked.size // 2
		packed[:pair_count] |= unpacked[1::2][:pair_count].astype(np.uint8) << 4
	if unpacked.size % 2:
		packed[-1] |= np.uint8(0xF0)
	return packed


def unpack_nibbles(packed: bytes | bytearray | np.ndarray, count: int | None = None) -> np.ndarray:
	"""Unpack low-nibble-first values, optionally truncating padding."""
	data = np.frombuffer(packed, dtype=np.uint8) if isinstance(packed, (bytes, bytearray)) else np.asarray(packed, dtype=np.uint8)
	values = np.empty(data.size * 2, dtype=np.uint8)
	values[::2] = data & 0x0F
	values[1::2] = data >> 4
	if count is not None:
		if not 0 <= count <= values.size:
			raise ValueError("Requested nibble count exceeds packed data")
		values = values[:count]
	return values