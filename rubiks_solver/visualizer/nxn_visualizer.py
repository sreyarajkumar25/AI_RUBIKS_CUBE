"""Interactive 3D NxN sticker renderer with move playback controls."""

from collections.abc import Sequence

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons, Slider
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

from rubiks_solver.core.cube_base import CubeBase
from rubiks_solver.core.cube_2x2 import Cube2x2
from rubiks_solver.core.cube_3x3 import Cube3x3
from rubiks_solver.core.cube_4x4 import Cube4x4
from rubiks_solver.core.cube_5x5 import Cube5x5
from rubiks_solver.moves.move_tables import NORMALS, _facelet_geometry, get_move_permutation
from rubiks_solver.moves.scramble import generate_scramble
from rubiks_solver.solvers.ida_star import SearchLimitExceeded
from rubiks_solver.solvers.solver_factory import Solver
from rubiks_solver.visualizer.ansi_fallback import render_ansi

FACE_COLORS = {
    "U": "#f8f7f2",
    "R": "#ff453a",
    "F": "#30d879",
    "D": "#ffe34d",
    "L": "#ff9638",
    "B": "#3998ff",
}
BACKGROUND = "#080d12"
BODY_COLOR = "#141d25"
TEXT_COLOR = "#eaf2f8"
TANGENTS = {
    "U": ((1, 0, 0), (0, 0, 1)),
    "R": ((0, 0, 1), (0, 1, 0)),
    "F": ((1, 0, 0), (0, 1, 0)),
    "D": ((1, 0, 0), (0, 0, 1)),
    "L": ((0, 0, 1), (0, 1, 0)),
    "B": ((1, 0, 0), (0, 1, 0)),
}


def _sticker_vertices(
    position: tuple[int, int, int], face: str
) -> list[tuple[float, float, float]]:
    first, second = TANGENTS[face]
    center = np.asarray(position, dtype=float) + np.asarray(NORMALS[face], dtype=float)
    first_vector = np.asarray(first, dtype=float) * 0.995
    second_vector = np.asarray(second, dtype=float) * 0.995
    return [
        tuple(center - first_vector - second_vector),
        tuple(center + first_vector - second_vector),
        tuple(center + first_vector + second_vector),
        tuple(center - first_vector + second_vector),
    ]


class Visualizer:
    def render(
        self,
        cube: CubeBase,
        solution: Sequence[str] = (),
        interval_ms: int = 500,
        show: bool = True,
    ) -> object | None:
        """Render a cube and optional move sequence with playback controls."""
        if not isinstance(cube, CubeBase):
            raise TypeError("Visualizer requires a CubeBase instance")
        if matplotlib.get_backend().lower() in {"agg", "pdf", "svg", "template"}:
            render_ansi(cube)
            return None

        working = cube.copy()
        initial_cube = cube.copy()
        moves = list(solution)
        current_size = cube.size
        index = 0
        playing = False
        celebration_started = False
        figure = plt.figure(figsize=(10, 8), facecolor=BACKGROUND)
        axes = figure.add_axes(
            (0.12, 0.2, 0.72, 0.76), projection="3d", computed_zorder=False
        )
        axes.view_init(elev=24, azim=38)
        axes.set_facecolor(BACKGROUND)
        timer = figure.canvas.new_timer(interval=interval_ms)
        timer.single_shot = False

        def draw(highlight: str | None = None) -> None:
            elevation, azimuth = axes.elev, axes.azim
            axes.clear()
            axes.set_facecolor(BACKGROUND)
            axes.computed_zorder = False
            geometry = _facelet_geometry(working.size)
            elevation_radians = np.deg2rad(elevation)
            azimuth_radians = np.deg2rad(azimuth)
            camera = np.asarray((
                np.cos(elevation_radians) * np.cos(azimuth_radians),
                np.cos(elevation_radians) * np.sin(azimuth_radians),
                np.sin(elevation_radians),
            ))
            face_normals = {
                "U": (0, 1, 0), "R": (1, 0, 0), "F": (0, 0, 1),
                "D": (0, -1, 0), "L": (-1, 0, 0), "B": (0, 0, -1),
            }
            visible_faces = {
                face for face, normal in face_normals.items()
                if np.dot(camera, normal) > 0.01
            }
            changed = set()
            if highlight is not None:
                permutation = get_move_permutation(working.size, highlight)
                changed = set(np.flatnonzero(permutation != np.arange(len(permutation))))
            face_polygons = {face: [] for face in visible_faces}
            face_colors = {face: [] for face in visible_faces}
            face_linewidths = {face: [] for face in visible_faces}
            for sticker_index, (position, normal) in enumerate(geometry):
                face = next(
                    candidate
                    for candidate, candidate_normal in face_normals.items()
                    if candidate_normal == normal
                )
                if face not in visible_faces:
                    continue
                face_polygons[face].append(_sticker_vertices(position, face))
                face_colors[face].append(FACE_COLORS[str(working.facelets[sticker_index])])
                face_linewidths[face].append(1.5 if sticker_index in changed else 0.35)
            for depth, face in enumerate(
                sorted(visible_faces, key=lambda face: np.dot(camera, face_normals[face]))
            ):
                collection = Poly3DCollection(
                    face_polygons[face],
                    facecolors=face_colors[face],
                    edgecolors="#101820",
                    linewidths=face_linewidths[face],
                    zsort="average",
                )
                collection.set_zorder(depth + 1)
                axes.add_collection3d(collection)
            extent = working.size
            axes.set(xlim=(-extent, extent), ylim=(-extent, extent), zlim=(-extent, extent))
            axes.set_box_aspect((1, 1, 1))
            axes.set_axis_off()
            axes.view_init(elev=elevation, azim=azimuth)
            axes.set_title(
                f"{working.size}x{working.size} cube  |  {index}/{len(moves)} moves",
                color=TEXT_COLOR,
                pad=12,
            )
            next_move = moves[index] if index < len(moves) else "complete" if moves else "not solved yet"
            status_text.set_text(f"Next: {next_move}   |   State: {'SOLVED' if working.is_solved() else 'SCRAMBLED'}")
            if moves:
                steps = [f"[{move}]" if step == index else move for step, move in enumerate(moves)]
                steps_text.set_text("Solution: " + " ".join(steps[:16]) + (" ..." if len(steps) > 16 else ""))
            else:
                steps_text.set_text("Solution: press Solve to calculate steps")
            figure.canvas.draw_idle()

        def step_forward(_event: object = None) -> None:
            nonlocal index, celebration_started
            if index < len(moves):
                move = moves[index]
                working.apply(move)
                index += 1
                draw(move)
                if index == len(moves) and working.is_solved() and not celebration_started:
                    celebration_started = True

                    def spin(frame: int) -> None:
                        axes.view_init(elev=24, azim=axes.azim + 1)
                        draw()

                    animation = FuncAnimation(
                        figure,
                        spin,
                        frames=range(360),
                        interval=20,
                        blit=False,
                    )
                    figure._rubiks_celebration = animation

        def step_backward(_event: object = None) -> None:
            nonlocal index
            if index > 0:
                move = moves[index - 1]
                inverse = move if move.endswith("2") else move[:-1] if move.endswith("'") else move + "'"
                working.apply(inverse)
                index -= 1
                draw(inverse)

        def toggle_play(_event: object = None) -> None:
            nonlocal playing
            playing = not playing
            if playing:
                timer.start()
            else:
                timer.stop()

        def advance() -> None:
            if index >= len(moves):
                timer.stop()
                return
            step_forward()

        timer.add_callback(advance)
        status_text = figure.text(0.12, 0.165, "", color=TEXT_COLOR, fontsize=9)
        steps_text = figure.text(0.12, 0.14, "", color=TEXT_COLOR, fontsize=8)
        play_axis = figure.add_axes((0.02, 0.065, 0.105, 0.06))
        back_axis = figure.add_axes((0.13, 0.065, 0.075, 0.06))
        step_axis = figure.add_axes((0.21, 0.065, 0.075, 0.06))
        reset_axis = figure.add_axes((0.29, 0.065, 0.075, 0.06))
        scramble_axis = figure.add_axes((0.37, 0.065, 0.105, 0.06))
        solve_axis = figure.add_axes((0.48, 0.065, 0.075, 0.06))
        help_axis = figure.add_axes((0.56, 0.065, 0.075, 0.06))
        speed_axis = figure.add_axes((0.69, 0.085, 0.16, 0.035))
        size_axis = figure.add_axes((0.86, 0.69, 0.11, 0.2), facecolor=BODY_COLOR)
        play_button = Button(play_axis, "Play / Pause", color=BODY_COLOR, hovercolor="#253645")
        back_button = Button(back_axis, "Back", color=BODY_COLOR, hovercolor="#253645")
        step_button = Button(step_axis, "Step", color=BODY_COLOR, hovercolor="#253645")
        reset_button = Button(reset_axis, "Reset", color=BODY_COLOR, hovercolor="#253645")
        scramble_button = Button(scramble_axis, "Scramble", color=BODY_COLOR, hovercolor="#253645")
        solve_button = Button(solve_axis, "Solve", color=BODY_COLOR, hovercolor="#253645")
        help_button = Button(help_axis, "Help", color=BODY_COLOR, hovercolor="#253645")
        speed_slider = Slider(
            speed_axis, "Speed", 100, 1200, valinit=interval_ms, valstep=50,
            color="#3998ff", track_color="#26333e",
        )
        sizes = (Cube2x2, Cube3x3, Cube4x4, Cube5x5)
        size_labels = ("2x2", "3x3", "4x4", "5x5")
        active_size = size_labels[cube.size - 2]
        size_selector = RadioButtons(
            size_axis, size_labels, active=size_labels.index(active_size),
            activecolor="#30d879",
        )
        figure.text(0.86, 0.91, "CUBE SIZE", color=TEXT_COLOR, fontsize=10, weight="bold")
        for button in (
            play_button, back_button, step_button, reset_button,
            scramble_button, solve_button, help_button,
        ):
            button.label.set_color(TEXT_COLOR)
        for label in size_selector.labels:
            label.set_color(TEXT_COLOR)
        speed_slider.label.set_color(TEXT_COLOR)
        speed_slider.valtext.set_color(TEXT_COLOR)
        play_button.on_clicked(toggle_play)
        back_button.on_clicked(step_backward)
        step_button.on_clicked(step_forward)

        def reset(_event: object = None) -> None:
            nonlocal index, working, celebration_started
            timer.stop()
            index = 0
            celebration_started = False
            working = initial_cube.copy()
            draw()

        def change_size(label: str) -> None:
            nonlocal index, working, initial_cube, moves, celebration_started, playing, current_size
            timer.stop()
            playing = False
            index = 0
            celebration_started = False
            current_size = int(label[0])
            initial_cube = sizes[current_size - 2]()
            moves = []
            working = initial_cube.copy()
            draw()

        def scramble(_event: object = None) -> None:
            nonlocal index, working, initial_cube, moves, celebration_started
            timer.stop()
            index = 0
            celebration_started = False
            scramble_lengths = {2: 7, 3: 5, 4: 3, 5: 2}
            initial_cube = sizes[current_size - 2]()
            initial_cube.apply_moves(generate_scramble(current_size, scramble_lengths[current_size]))
            working = initial_cube.copy()
            moves = []
            draw()

        def solve(_event: object = None) -> None:
            nonlocal index, working, moves, celebration_started
            timer.stop()
            index = 0
            celebration_started = False
            try:
                solver_options = {"max_depth": 12, "max_nodes": 300_000}
                moves = Solver("ida_star", **solver_options).solve(initial_cube.copy())
            except SearchLimitExceeded as error:
                moves = []
                status_text.set_text(f"Could not solve within limits: {error}")
            working = initial_cube.copy()
            draw()

        def show_help(_event: object = None) -> None:
            help_figure = plt.figure(figsize=(6, 4), facecolor=BACKGROUND)
            help_axes = help_figure.add_axes((0.08, 0.08, 0.84, 0.84))
            help_axes.set_facecolor(BACKGROUND)
            help_axes.axis("off")
            help_axes.text(
                0.02, 0.98,
                "CUBE VIEWER HELP\n\n"
                "Choose 2x2, 3x3, 4x4, or 5x5 in the size selector. Changing size\n"
                "loads a solved cube. Scramble creates a new random start state;\n"
                "Solve calculates a solution for the current state.\n\n"
                "Drag on the cube to orbit. Use the mouse wheel to zoom.\n"
                "Step applies one solution move; Back undoes one; Play / Pause\n"
                "runs the sequence; Reset returns to the scramble state.\n"
                "Adjust Speed to change playback delay.\n\n"
                "The active move is shown in brackets in the solution line.\n"
                "The displayed color state is not changed by orbiting the camera.",
                va="top", color=TEXT_COLOR, fontsize=11, linespacing=1.5,
            )
            help_figure._rubiks_help = True
            help_figure.show()

        def refresh_camera(_event: object = None) -> None:
            draw()

        reset_button.on_clicked(reset)
        scramble_button.on_clicked(scramble)
        solve_button.on_clicked(solve)
        help_button.on_clicked(show_help)
        size_selector.on_clicked(change_size)
        speed_slider.on_changed(lambda value: setattr(timer, "interval", int(value)))
        figure.canvas.mpl_connect("button_release_event", refresh_camera)
        figure.canvas.mpl_connect("scroll_event", refresh_camera)
        draw()
        figure._rubiks_redraw = draw
        figure._rubiks_controls = (
            play_button, back_button, step_button, reset_button, scramble_button,
            solve_button, help_button, speed_slider, size_selector, timer,
        )
        if show:
            plt.show()
        return figure

    def celebrate(self, cube: CubeBase, show: bool = True) -> object | None:
        """Animate a full camera revolution around a solved cube."""
        figure = self.render(cube, show=False)
        if figure is None:
            return None
        axes = figure.axes[0]

        def spin(frame: int) -> None:
            axes.view_init(elev=24, azim=38 + frame)
            figure._rubiks_redraw()

        animation = FuncAnimation(
            figure,
            spin,
            frames=range(360),
            interval=20,
            blit=False,
        )
        figure._rubiks_celebration = animation
        if show:
            plt.show()
        return figure