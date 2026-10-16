"""Interactive 3D NxN sticker renderer with move playback controls."""

from collections.abc import Sequence

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

from rubiks_solver.core.cube_base import CubeBase
from rubiks_solver.moves.move_tables import _facelet_geometry, get_move_permutation
from rubiks_solver.visualizer.ansi_fallback import render_ansi

FACE_COLORS = {
    "U": "#f4f2e9",
    "R": "#d64136",
    "F": "#258b57",
    "D": "#f2c94c",
    "L": "#ef8737",
    "B": "#3478b8",
}
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
    center = np.asarray(position, dtype=float)
    first_vector = np.asarray(first, dtype=float) * 0.91
    second_vector = np.asarray(second, dtype=float) * 0.91
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
        moves = tuple(solution)
        index = 0
        playing = False
        celebration_started = False
        figure = plt.figure(figsize=(8, 7))
        axes = figure.add_axes((0.03, 0.19, 0.94, 0.78), projection="3d")
        axes.view_init(elev=24, azim=38)
        timer = figure.canvas.new_timer(interval=interval_ms)
        timer.single_shot = False

        def draw(highlight: str | None = None) -> None:
            elevation, azimuth = axes.elev, axes.azim
            axes.clear()
            geometry = _facelet_geometry(working.size)
            changed = set()
            if highlight is not None:
                permutation = get_move_permutation(working.size, highlight)
                changed = set(np.flatnonzero(permutation != np.arange(len(permutation))))
            for sticker_index, (position, normal) in enumerate(geometry):
                face_index = sticker_index // (working.size * working.size)
                face = next(
                    candidate
                    for candidate, candidate_normal in {
                        "U": (0, 1, 0), "R": (1, 0, 0), "F": (0, 0, 1),
                        "D": (0, -1, 0), "L": (-1, 0, 0), "B": (0, 0, -1),
                    }.items()
                    if candidate_normal == normal
                )
                color = FACE_COLORS[str(working.facelets[sticker_index])]
                polygon = Poly3DCollection(
                    [_sticker_vertices(position, face)],
                    facecolors=color,
                    edgecolors="#f4f2e9" if sticker_index in changed else "#252a31",
                    linewidths=1.8 if sticker_index in changed else 1.0,
                )
                axes.add_collection3d(polygon)
            bound = working.size
            axes.set(xlim=(-bound, bound), ylim=(-bound, bound), zlim=(-bound, bound))
            axes.set_box_aspect((1, 1, 1))
            axes.set_axis_off()
            axes.view_init(elev=elevation, azim=azimuth)
            axes.set_title(
                f"{working.size}x{working.size} cube  |  {index}/{len(moves)} moves",
                pad=12,
            )
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
                    animation = FuncAnimation(
                        figure,
                        lambda frame: axes.view_init(elev=24, azim=axes.azim + 1),
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
        play_axis = figure.add_axes((0.05, 0.08, 0.18, 0.06))
        back_axis = figure.add_axes((0.25, 0.08, 0.12, 0.06))
        step_axis = figure.add_axes((0.39, 0.08, 0.12, 0.06))
        reset_axis = figure.add_axes((0.53, 0.08, 0.12, 0.06))
        speed_axis = figure.add_axes((0.72, 0.09, 0.23, 0.04))
        play_button = Button(play_axis, "Play / Pause")
        back_button = Button(back_axis, "Back")
        step_button = Button(step_axis, "Step")
        reset_button = Button(reset_axis, "Reset")
        speed_slider = Slider(speed_axis, "Speed", 100, 1200, valinit=interval_ms, valstep=50)
        play_button.on_clicked(toggle_play)
        back_button.on_clicked(step_backward)
        step_button.on_clicked(step_forward)

        def reset(_event: object = None) -> None:
            nonlocal index, working
            timer.stop()
            index = 0
            working = cube.copy()
            draw()

        reset_button.on_clicked(reset)
        speed_slider.on_changed(lambda value: setattr(timer, "interval", int(value)))
        draw()
        figure._rubiks_controls = (play_button, back_button, step_button, reset_button, speed_slider, timer)
        if show:
            plt.show()
        return figure

    def celebrate(self, cube: CubeBase, show: bool = True) -> object | None:
        """Animate a full camera revolution around a solved cube."""
        figure = self.render(cube, show=False)
        if figure is None:
            return None
        axes = figure.axes[0]
        animation = FuncAnimation(
            figure,
            lambda frame: axes.view_init(elev=24, azim=38 + frame),
            frames=range(360),
            interval=20,
            blit=False,
        )
        figure._rubiks_celebration = animation
        if show:
            plt.show()
        return figure