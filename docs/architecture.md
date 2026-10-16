# Architecture

The package is organized into cube models, move handling, search, heuristics,
large-cube reduction, visualization, and CLI layers. The intended pipeline is
to validate a facelet state, solve directly for 2x2 and 3x3 cubes, and reduce
larger cubes before handing the resulting state to a 3x3 solver.

The current release is a scaffold. Only solved-state facelet models, basic
move notation listing, and CLI argument handling are implemented.