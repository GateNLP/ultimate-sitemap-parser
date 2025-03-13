import shlex

import pytest

from usp.cli.cli import main as cli_main


@pytest.fixture
def run_cmd(capsys):
    def _run_cmd(args, expected_exit=0):
        args = shlex.split(args)
        with pytest.raises(SystemExit) as excinfo:
            cli_main(args)
        assert excinfo.value.code == expected_exit
        outerr = capsys.readouterr()
        out = outerr.out.rstrip()
        err = outerr.err.rstrip()
        return out, err

    return _run_cmd
