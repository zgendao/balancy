import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


ENV_WEB3_PROVIDER = "WEB3_PROVIDER_URL"
ENV_DB_URI = "DB_URI"
DEFAULT_WEB3_PROVIDER = "ws://127.0.0.1:8545"
DEFAULT_DB_URI = "http://127.0.0.1:2379"
DOTENV_FILENAME = ".env"


@dataclass
class EnvVar:
    key: str
    val: str
    set: bool = False


class EnvConfig:
    def __init__(self):
        w3url = os.getenv(ENV_WEB3_PROVIDER)
        self.WEB3_PROVIDER_URL = w3url if w3url else DEFAULT_WEB3_PROVIDER

        db_uri = os.getenv(ENV_DB_URI)
        self.DB_URI = db_uri if db_uri else DEFAULT_DB_URI

    @classmethod
    def set_environment(
        cls, w3url: Optional[str] = None, db_uri: Optional[str] = None
    ) -> None:
        if w3url:
            os.environ[ENV_WEB3_PROVIDER] = w3url
        if db_uri:
            os.environ[ENV_DB_URI] = db_uri

    @classmethod
    def set_defaults(
        cls, w3url: Optional[str] = None, db_uri: Optional[str] = None
    ) -> None:
        env_vars: List[EnvVar] = []
        if w3url:
            env_vars.append(EnvVar(ENV_WEB3_PROVIDER, w3url))
        if db_uri:
            env_vars.append(EnvVar(ENV_DB_URI, db_uri))
        if len(env_vars) > 0:
            _put_in_env_file(env_vars)


def _put_in_env_file(env_vars: List[EnvVar], filename: str = DOTENV_FILENAME) -> None:
    try:
        with open(filename, "r") as file:
            lines = list(file.readlines())
    except FileNotFoundError:
        lines = []
    new_lines = _replace_or_append_env_vars(env_vars, lines)
    with open(filename, "w") as file:
        file.writelines(new_lines)


def _replace_or_append_env_vars(
    env_vars: List[EnvVar], file_lines: List[str]
) -> List[str]:
    new_lines = [*file_lines]
    for i, line in enumerate(file_lines):
        key_in_line, _ = line.split("=")
        for ev in env_vars:
            if ev.key == key_in_line and not ev.set:
                new_lines[i] = f"{ev.key}={ev.val}\n"
                ev.set = True
                break
    for ev in env_vars:
        if not ev.set:
            new_lines.append(f"{ev.key}={ev.val}\n")
    return new_lines
