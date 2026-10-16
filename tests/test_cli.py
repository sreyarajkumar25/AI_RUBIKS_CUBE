from rubiks_solver.cli.commands import main


def test_cli_without_command_prints_help(capsys):
    assert main([]) == 0
    assert "usage:" in capsys.readouterr().out


def test_cli_solves_reduced_large_cube(capsys):
    assert main(["solve", "--scramble", "R U", "--size", "4"]) == 0
    assert "Solution:" in capsys.readouterr().out