import getpass
import os
import shlex
import sys

import paramiko


HOST = os.getenv("LAB1_HOST", "192.168.239.141")
USER = os.getenv("LAB1_USER", "mah")
RUNNER_DIR = "/home/mah/actions-runner-devmon"
SOURCE_RUNNER_DIR = "/home/mah/actions-runner-progress-tracker"
RUNNER_TARBALL = f"{SOURCE_RUNNER_DIR}/actions-runner-linux-x64.tar.gz"
REPO_URL = "https://github.com/mahamahseb/DevMon"


def main() -> int:
    ssh_password = os.getenv("LAB1_SSH_PASSWORD") or getpass.getpass("LAB1 SSH password: ")
    runner_token = os.getenv("DEVMON_RUNNER_TOKEN") or getpass.getpass("DevMon runner registration token: ")
    if not runner_token:
        print("Missing DEVMON_RUNNER_TOKEN", file=sys.stderr)
        return 2

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=HOST,
        username=USER,
        password=ssh_password,
        timeout=10,
        auth_timeout=10,
        banner_timeout=10,
        look_for_keys=False,
        allow_agent=False,
    )
    try:
        run(client, f"test -d {shlex.quote(SOURCE_RUNNER_DIR)}")
        run(client, f"test -f {shlex.quote(RUNNER_TARBALL)}")
        run(client, f"pids=$(pgrep -f '{RUNNER_DIR}/bin/[R]unner.Listener' || true); if [ -n \"$pids\" ]; then kill $pids; fi")
        run(
            client,
            "set -eu; "
            f"if [ -d {shlex.quote(RUNNER_DIR)} ]; then "
            f"mv {shlex.quote(RUNNER_DIR)} {shlex.quote(RUNNER_DIR)}.stale-$(date +%Y%m%d%H%M%S); "
            "fi; "
            f"mkdir -p {shlex.quote(RUNNER_DIR)}; "
            f"tar -xzf {shlex.quote(RUNNER_TARBALL)} -C {shlex.quote(RUNNER_DIR)}",
        )
        config_command = (
            f"cd {shlex.quote(RUNNER_DIR)} && "
            "./config.sh --unattended "
            f"--url {shlex.quote(REPO_URL)} "
            f"--token {shlex.quote(runner_token)} "
            "--name devmon-minikube "
            "--labels self-hosted,linux,minikube "
            "--work _work "
            "--replace"
        )
        run(client, "getent hosts github.com && getent hosts pipelines.actions.githubusercontent.com || true")
        run_with_retries(client, config_command, redact=runner_token)
        run(client, "pkill -f '/home/mah/actions-runner-devmon/bin/Runner.Listener' || true")
        run(client, f"cd {shlex.quote(RUNNER_DIR)} && nohup ./run.sh > runner.log 2>&1 &")
        run(client, "sleep 2; ps -ef | grep '/home/mah/actions-runner-devmon/bin/Runner.Listener' | grep -v grep || true")
    finally:
        client.close()

    return 0


def run(client: paramiko.SSHClient, command: str, redact: str | None = None) -> None:
    display = command.replace(redact, "***") if redact else command
    print(f"\n$ {display}")
    stdin, stdout, stderr = client.exec_command(command, timeout=120)
    del stdin
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    if out:
        print(out)
    if err:
        print("STDERR:", err)
    print("exit:", code)
    if code != 0:
        raise RuntimeError(f"Command failed: {display}")


def run_with_retries(client: paramiko.SSHClient, command: str, redact: str | None = None, attempts: int = 3) -> None:
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            run(client, command, redact=redact)
            return
        except RuntimeError as exc:
            last_error = exc
            if attempt == attempts:
                break
            print(f"retrying after failed attempt {attempt}/{attempts}...")
            run(client, "sleep 5")
    raise last_error


if __name__ == "__main__":
    raise SystemExit(main())
