import pytest
from click.testing import CliRunner


@pytest.fixture()
def cli_runner():
    # Setup
    runner = CliRunner()
    yield runner
    # Tear Down


def test_self_can_startup_well(cli_runner):
    import dragon
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(dragon.cli, '--help')
    assert result.exit_code == 0
    assert 'Usage:' in result.stdout


def test_sub_cmd_can_startup_well(cli_runner):
    from cmds import cmd_project
    from cmds import cmd_blog
    results = []
    with cli_runner.isolated_filesystem():
        results.append(cli_runner.invoke(cmd_project.cli, '--help'))
        results.append(cli_runner.invoke(cmd_blog.cli, '--help'))

    for result in results:
        assert result.exit_code == 0
        assert 'Usage:' in result.stdout