from unittest.mock import patch

from rubiks_solver.core.cube_3x3 import Cube3x3
from rubiks_solver.core.cube_4x4 import Cube4x4
from rubiks_solver.moves.scramble import generate_scramble
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
	assert len(figure.axes[0].collections) == 3
	assert len(figure._rubiks_controls) == 10
	selector = figure._rubiks_controls[8]
	selector.set_active(3)
	assert "5x5 cube" in figure.axes[0].get_title()
	assert len(figure.axes[0].collections) == 3
	assert figure.get_facecolor()[:3] == (8 / 255, 13 / 255, 18 / 255)


def test_scramble_solve_and_step_controls_preserve_cube_state():
	cube = Cube3x3()
	original_state = cube.state_key()
	with patch("matplotlib.get_backend", return_value="TkAgg"):
		figure = Visualizer().render(cube, show=False)
	scramble_button = figure._rubiks_controls[4]
	solve_button = figure._rubiks_controls[5]
	step_button = figure._rubiks_controls[2]
	scramble_button._observers.process("clicked", None)
	scrambled_title = figure.axes[0].get_title()
	assert "New scramble ready" in figure.texts[0].get_text()
	assert cube.state_key() == original_state
	solve_button._observers.process("clicked", None)
	assert "Solution:" in figure.texts[1].get_text()
	step_button._observers.process("clicked", None)
	assert figure.axes[0].get_title() != scrambled_title
	assert cube.state_key() == original_state
	figure.axes[0].view_init(elev=45, azim=135)
	figure._rubiks_redraw()
	assert cube.state_key() == original_state


def test_solve_and_step_reach_solved_state_and_play_pause_labels_update():
	cube = Cube3x3().apply("R")
	with patch("matplotlib.get_backend", return_value="TkAgg"):
		figure = Visualizer().render(cube, show=False)
	solve_button = figure._rubiks_controls[5]
	play_button = figure._rubiks_controls[0]
	step_button = figure._rubiks_controls[2]
	solve_button._observers.process("clicked", None)
	assert "Solution found: 1 move" in figure.texts[0].get_text()
	assert "[R']" in figure.texts[1].get_text()
	play_button._observers.process("clicked", None)
	assert play_button.label.get_text() == "Pause"
	play_button._observers.process("clicked", None)
	assert play_button.label.get_text() == "Play"
	step_button._observers.process("clicked", None)
	assert "SOLVED" in figure.texts[0].get_text()
	assert "1/1 moves" in figure.axes[0].get_title()


def test_scramble_generator_returns_requested_number_of_moves():
	scramble = generate_scramble(4, 12, seed=7)
	assert len(scramble) == 12
	assert scramble == generate_scramble(4, 12, seed=7)