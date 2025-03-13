import pytest


@pytest.mark.parametrize("command", ["", "-h", "--help"])
def test_help(run_cmd, command):
    out, _ = run_cmd(command)
    assert out.startswith("usage: usp [-h] [-v]  ...")
