import os

import pytest

from app import config
from app.config import EnvConfig, EnvVar, _replace_or_append_env_vars


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


@pytest.mark.parametrize(
    "env_key, env_default_value",
    [
        (config.ENV_WEB3_PROVIDER, config.DEFAULT_WEB3_PROVIDER),
        (config.ENV_DB_URI, config.DEFAULT_DB_URI),
    ],
)
class TestEnvConfigInit:
    def test_env_var_none(self, env_key, env_default_value):
        del os.environ[env_key]
        env_config = EnvConfig()
        assert getattr(env_config, env_key) == env_default_value

    def test_env_var_not_none(self, env_key, env_default_value):
        expected_value = "some value"
        os.environ[env_key] = expected_value
        env_config = EnvConfig()
        assert getattr(env_config, env_key) == expected_value
