from typer.testing import CliRunner

from app import cli

runner = CliRunner()


def test_say_hello(capsys):
    result = runner.invoke(cli, ["say-hello"])
    assert result.exit_code == 0
    assert "Hi!" in result.stdout


def test_say_hello_with_text(capsys):
    result = runner.invoke(cli, ["say-hello", "--text", "Hello there"])
    assert result.exit_code == 0
    assert "General Kenobi!" in result.stdout
