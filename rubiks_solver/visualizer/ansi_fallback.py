"""Simple ANSI face-grid rendering for headless environments."""

from rubiks_solver.core.cube_base import CubeBase

ANSI = {
	"U": "\033[97m",
	"R": "\033[91m",
	"F": "\033[92m",
	"D": "\033[93m",
	"L": "\033[38;5;208m",
	"B": "\033[94m",
}
RESET = "\033[0m"


def render_ansi(cube: CubeBase, color: bool = True) -> str:
	face_area = cube.size * cube.size
	rendered = []
	for face_index, face in enumerate(CubeBase.FACES):
		start = face_index * face_area
		stickers = cube.facelets[start : start + face_area]
		rows = []
		for row in range(cube.size):
			cells = []
			for sticker in stickers[row * cube.size : (row + 1) * cube.size]:
				value = str(sticker)
				cells.append(f"{ANSI.get(value, '')}{value}{RESET}" if color else value)
			rows.append(" ".join(cells))
		rendered.append(f"{face}:\n" + "\n".join(rows))
	output = "\n\n".join(rendered)
	print(output)
	return output