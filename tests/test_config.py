from app.config import EnvVar, _replace_or_append_env_vars


def test_replace_or_append_env_vars():
    env_vars = [EnvVar("key1", "val1"), EnvVar("key2", "val2")]
    file_lines = ["key2=replace_this\n", "other_key=leave_this\n"]
    expected_lines = ["key2=val2\n", "other_key=leave_this\n", "key1=val1\n"]
    result_lines = _replace_or_append_env_vars(env_vars, file_lines)
    assert expected_lines == result_lines


def test_replace_or_appenv_env_vars_no_file():
    env_vars = [EnvVar("key1", "val1"), EnvVar("key2", "val2")]
    expected_lines = ["key1=val1\n", "key2=val2\n"]
    result_lines = _replace_or_append_env_vars(env_vars, [])
    assert expected_lines == result_lines
