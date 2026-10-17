def assert_usage(result, log_path):
    assert result.code == 2
    assert result.out == ""
    assert "usage" in result.err.lower()
    assert not log_path.exists()


def test_no_arguments_shows_usage_exit_2(run_cli, log_path):
    assert_usage(run_cli(), log_path)


def test_one_argument_shows_usage_exit_2(run_cli, log_path):
    assert_usage(run_cli("100"), log_path)


def test_extra_argument_shows_usage_exit_2(run_cli, log_path):
    assert_usage(run_cli("100", "US", "extra"), log_path)


def test_help_option_shows_usage_exit_0(run_cli, log_path):
    # -h and --help are the one exception to "a leading - is always the amount" (FR-022).
    for argv in (("-h",), ("--help",), ("-h", "US"), ("100", "--help")):
        result = run_cli(*argv)
        assert result.code == 0, argv
        assert "usage" in result.out.lower(), argv
        assert "INR" not in result.out, argv
        assert result.err == "", argv
    assert not log_path.exists()
