from app import say_hello


def test_app(capsys):
    say_hello()
    captured = capsys.readouterr()
    assert captured.out == "Hello World!\n"
