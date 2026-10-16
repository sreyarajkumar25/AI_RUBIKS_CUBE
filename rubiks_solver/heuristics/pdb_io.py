"""Read and write compact unsigned-byte pattern database files."""

from pathlib import Path

import numpy as np

from rubiks_solver.utils.bitpacking import pack_nibbles


class NibbleTable:
	"""Memory-mapped 4-bit lookup table with integer indexing."""

	def __init__(self, path: str | Path, size: int) -> None:
		self.packed = np.memmap(path, mode="r", dtype=np.uint8)
		if self.packed.size != (size + 1) // 2:
			raise ValueError("Packed PDB file size does not match its entry count")
		self.size = size

	def __len__(self) -> int:
		return self.size

	def __getitem__(self, index: int) -> int:
		if not 0 <= index < self.size:
			raise IndexError("PDB index out of range")
		value = int(self.packed[index // 2])
		return (value >> (4 * (index & 1))) & 0x0F


def save_pdb(path: str | Path, values: np.ndarray) -> None:
	"""Save nibble-sized distances to a compact binary file."""
	pack_nibbles(values).tofile(path)


def load_pdb(path: str | Path, expected_size: int) -> NibbleTable:
	"""Memory-map a packed distance table and verify its number of entries."""
	return NibbleTable(path, expected_size)