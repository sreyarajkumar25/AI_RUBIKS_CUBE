from unittest.mock import patch

from rubiks_solver.core.cube_4x4 import Cube4x4
from rubiks_solver.visualizer.ansi_fallback import render_ansi
from rubiks_solver.visualizer.nxn_visualizer import Visualizer


def test_ansi_renderer_supports_dynamic_cube_size(capsys):
	output = render_ansi(Cube4x4(), color=False)
	assert output.count("\n") >= 24
	assert "U:" in capsys.readouterr().out


def test_matplotlib_renderer_builds_dynamic_sticker_grid():
	with patch("matplotlib.get_backend", return_value="TkAgg"):
		figure = Visualizer().render(Cube4x4(), ("Rw",), show=False)
	assert figure is not None
	assert len(figure.axes[0].collections) == 96
	assert len(figure._rubiks_controls) == 6