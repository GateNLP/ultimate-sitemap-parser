import pytest


def test_root_command(run_cmd):
    out, err = run_cmd("ls", expected_exit=2)
    assert err.startswith("usage: usp ls")


@pytest.mark.parametrize("expected_out", ["-h", "--help"])
def test_help(run_cmd, expected_out):
    out, _ = run_cmd(
        f"ls {expected_out}",
    )
    assert out.startswith("usage: usp ls")


@pytest.fixture
def mock_sitemap_tree(mocker):
    mock_tree = mocker.Mock()
    mock_tree.url = "https://example.org"
    mock_fn = mocker.patch("usp.cli._ls.sitemap_tree_for_homepage")
    mock_fn.return_value = mock_tree
    return mock_fn


@pytest.fixture(autouse=True)
def mock_output_tabtree(mocker):
    return mocker.patch("usp.cli._ls._output_sitemap_nested")


@pytest.fixture(autouse=True)
def mock_output_pages(mocker):
    return mocker.patch("usp.cli._ls._output_pages")


def test_simple(run_cmd, mock_sitemap_tree, mock_output_tabtree, mock_output_pages):
    run_cmd("ls https://example.org")

    mock_sitemap_tree.assert_called_once_with(
        "https://example.org", use_robots=True, use_known_paths=True
    )
    mock_output_tabtree.assert_called_once_with(mock_sitemap_tree.return_value, "")
    mock_output_pages.assert_not_called()


@pytest.mark.parametrize(
    ("robot_arg", "exp_robot_val"), [("", True), ("-r", False), ("--no-robots", False)]
)
@pytest.mark.parametrize(
    ("known_paths_arg", "exp_known_paths_val"),
    [("", True), ("-k", False), ("--no-known", False)],
)
def test_discovery_args(
    run_cmd,
    mock_sitemap_tree,
    robot_arg,
    exp_robot_val,
    known_paths_arg,
    exp_known_paths_val,
):
    run_cmd(f"ls https://example.org {robot_arg} {known_paths_arg}")
    mock_sitemap_tree.assert_called_once_with(
        "https://example.org",
        use_robots=exp_robot_val,
        use_known_paths=exp_known_paths_val,
    )


@pytest.mark.parametrize(
    ("arg", "exp_pg_calls", "exp_tt_calls"),
    [
        ("", 0, 1),
        ("-f pages", 1, 0),
        ("--format pages", 1, 0),
        ("-f tabtree", 0, 1),
        ("--format tabtree", 0, 1),
    ],
)
def test_format(
    run_cmd,
    mock_sitemap_tree,
    mock_output_pages,
    mock_output_tabtree,
    arg,
    exp_pg_calls,
    exp_tt_calls,
):
    run_cmd(f"ls https://example.org {arg}")

    assert mock_output_pages.call_count == exp_pg_calls
    assert mock_output_tabtree.call_count == exp_tt_calls


@pytest.mark.parametrize("arg", ["-u", "--strip-url"])
def test_strip_url(run_cmd, mock_sitemap_tree, mock_output_tabtree, arg):
    run_cmd(f"ls https://example.org {arg}")

    mock_output_tabtree.assert_called_once_with(
        mock_sitemap_tree.return_value, "https://example.org"
    )


@pytest.mark.parametrize(
    ("v_arg", "exp_lvl"),
    [("", 0), ("-v", 1), ("--verbose", 1), ("-vv", 2), ("--verbose --verbose", 2)],
)
@pytest.mark.parametrize(
    ("l_arg", "exp_file_name"),
    [("", None), ("-l log.txt", "log.txt"), ("--log-file log.txt", "log.txt")],
)
def test_log_verbosity(
    run_cmd, mocker, mock_sitemap_tree, v_arg, exp_lvl, l_arg, exp_file_name
):
    mock_logging = mocker.patch("usp.cli._ls.setup_logging")
    run_cmd(f"ls https://example.org {v_arg} {l_arg}")

    mock_logging.assert_called_once_with(exp_lvl, exp_file_name)
