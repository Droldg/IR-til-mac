#!/usr/bin/env python3
import argparse
import os
import platform
import shlex
import subprocess
import sys
from pathlib import Path


SERVICE_NAME = "pico-ir-listener.service"


def service_dir():
    return Path.home() / ".config" / "systemd" / "user"


def service_path():
    return service_dir() / SERVICE_NAME


def listener_dir():
    return Path(__file__).resolve().parent


def python_executable():
    return sys.executable or "/usr/bin/python3"


def service_text():
    script_path = listener_dir() / "listener.py"
    command = "cd {directory} && exec {python} {script}".format(
        directory=shlex.quote(str(listener_dir())),
        python=shlex.quote(python_executable()),
        script=shlex.quote(str(script_path)),
    )
    return """[Unit]
Description=Pico IR shutdown listener

[Service]
ExecStart=/bin/sh -c {command}
Restart=always
RestartSec=2

[Install]
WantedBy=default.target
""".format(
        command=shlex.quote(command),
    )


def run_systemctl(*args):
    return subprocess.run(
        ["systemctl", "--user", *args],
        check=False,
    ).returncode


def install_service(start):
    service_dir().mkdir(parents=True, exist_ok=True)
    service_path().write_text(service_text(), encoding="utf-8")

    if run_systemctl("daemon-reload") != 0:
        return 1

    if start:
        code = run_systemctl("enable", "--now", SERVICE_NAME)
    else:
        code = run_systemctl("enable", SERVICE_NAME)

    if code != 0:
        return code

    print("Installed Linux user service:")
    print(service_path())
    return 0


def uninstall_service():
    run_systemctl("disable", "--now", SERVICE_NAME)

    path = service_path()
    if path.exists():
        path.unlink()

    run_systemctl("daemon-reload")
    print("Removed Linux user service:")
    print(path)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Install or uninstall the Pico IR listener Linux user service."
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove the Linux user service instead of installing it.",
    )
    parser.add_argument(
        "--no-start",
        action="store_true",
        help="Install and enable the service without starting it now.",
    )
    args = parser.parse_args()

    if os.name != "posix" or platform.system() != "Linux":
        print("This script is for Linux systems with systemd user services.", file=sys.stderr)
        return 1

    if args.uninstall:
        return uninstall_service()

    return install_service(not args.no_start)


if __name__ == "__main__":
    raise SystemExit(main())
