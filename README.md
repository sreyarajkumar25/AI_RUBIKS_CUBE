# Rubik's Cube Solver

Python 3.10+ package for representing NxN Rubik's cubes (2x2 through 5x5),
applying face, wide, and inner-slice turns, and searching for solutions with
IDA* or bidirectional breadth-first search. Facelet turns use cached NumPy
permutations. The package also includes a dynamic Matplotlib renderer and
facelet-based reduction checks for 4x4 and 5x5 cubes.

## Install

```bash
python -m pip install -e '.[test]'
```

For runtime dependencies only, use `python -m pip install -e .`. NumPy powers
cube and move state; Matplotlib is used by the interactive visualizer.

## Quick Start

```python
from rubiks_solver import Cube
from rubiks_solver.solvers.solver_factory import Solver

cube = Cube().apply_moves(("R", "U"))
solution = Solver("ida_star").solve(cube)
cube.apply_moves(solution)
assert cube.is_solved()
```

Select the alternate search engine with `Solver("bidirectional")`. Both
engines accept any `CubeBase` subclass and return a list of move tokens.

## CLI

```bash
python -m rubiks_solver --help
python -m rubiks_solver solve --scramble "R U" --size 3 --algo ida_star
python -m rubiks_solver scramble --size 5 --moves 40
python -m rubiks_solver benchmark --size 3 --trials 10
```

The `solve` command accepts `--visualize` to play back a solution. `--algo`
accepts `ida_star` or `bidirectional`. `generate-pdb` currently reports that
database generation is unavailable; no precomputed database files are shipped.

## Supported Behavior

- Cube models store exactly `6 * N * N` facelets for sizes 2 through 5.
- Move tables are generated geometrically and cached per size. Wide turns and
	individual inner slices are available for sizes 4 and 5.
- IDA* is optimal within its configured depth/node limits and uses an
	admissible displaced-piece lower bound for corners and 3x3 edges.
- Bidirectional BFS expands the smaller frontier and is optimal within its
	search limits. It is intended for short scrambles due to memory growth.
- 4x4/5x5 facelets can be reduced to a 3x3 state only after centers are
	monochromatic and each edge's wings are paired. `Reducer.solve` then solves
	that reduced state. When reduction checks fail, it falls back to bounded
	direct search, which can solve shallow unreduced states but is not a
	substitute for the full center/edge reduction method.
- The visualizer supports orbit/zoom, play, pause, step, back, reset, speed,
	sticker highlighting, and an ANSI fallback when using a headless backend.

## Current Limitations

This is not yet a complete deep-scramble solver. The corner/edge PDB coordinate
ranking and file readers exist, but full database generation and lookup
integration are not implemented. Search therefore becomes impractical on
long 3x3 scrambles. The package does not yet solve centers or pair wings on an
arbitrary 4x4/5x5 state, nor does it apply OLL/PLL parity algorithms. For those
sizes, deep non-reduced states may exceed the direct-search limits.

## Development

```bash
python -m pytest
python -m unittest discover -v
```

See `docs/` for architecture and algorithm notes.