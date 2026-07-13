import os
from dataclasses import dataclass

import paramiko

from . import config


@dataclass
class CommandResult:
    command: str
    stdout: str
    stderr: str
    exit_status: int


class ReadOnlySSHClient:
    def __init__(self, target: config.ServerTarget):
        self.target = target

    def run_commands(self, commands: list[str]) -> list[CommandResult]:
        self._validate_commands(commands)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(**self._connect_kwargs())
            return [self._run_one(client, command) for command in commands]
        finally:
            client.close()

    def _connect_kwargs(self) -> dict:
        password = os.getenv(config.SSH_PASSWORD_ENV)
        key_path = os.getenv(config.SSH_KEY_PATH_ENV)
        kwargs = {
            "hostname": self.target.host,
            "username": self.target.user,
            "timeout": 10,
            "auth_timeout": 10,
            "banner_timeout": 10,
            "look_for_keys": False,
            "allow_agent": False,
        }
        if key_path:
            kwargs["key_filename"] = key_path
        else:
            kwargs["password"] = password
        return kwargs

    def _run_one(self, client: paramiko.SSHClient, command: str) -> CommandResult:
        stdin, stdout, stderr = client.exec_command(command, timeout=40)
        del stdin
        exit_status = stdout.channel.recv_exit_status()
        return CommandResult(
            command=command,
            stdout=stdout.read().decode("utf-8", errors="replace").strip(),
            stderr=stderr.read().decode("utf-8", errors="replace").strip(),
            exit_status=exit_status,
        )

    def _validate_commands(self, commands: list[str]) -> None:
        allowed = set(config.TRAFFIC_COMMANDS + config.DEPLOY_COMMANDS)
        unknown = [command for command in commands if command not in allowed]
        if unknown:
            raise ValueError(f"Blocked non-allowlisted command: {unknown[0]}")
