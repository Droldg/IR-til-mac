import argparse
import platform
import subprocess
import sys
import time

import serial
from serial import SerialException
from serial.tools import list_ports


BAUD_RATE = 115200
TRIGGER = "SHUTDOWN"
RETRY_SECONDS = 2
OLD_PICO_COMMANDS = {
    "sudo shutdown now",
    "sudo /usr/bin/shutdown now",
    "sudo /sbin/shutdown now",
}


def find_port():
    ports = list(list_ports.comports())
    if len(ports) == 1:
        return ports[0].device

    pico_matches = [
        port.device
        for port in ports
        if "pico" in (port.description or "").lower()
        or "rp2040" in (port.description or "").lower()
    ]

    if len(pico_matches) == 1:
        return pico_matches[0]

    return None


def available_ports_text():
    ports = list(list_ports.comports())
    if not ports:
        return "none"

    return ", ".join(
        "{} ({})".format(item.device, item.description) for item in ports
    )


def shutdown_command():
    system = platform.system()

    if system == "Windows":
        return ["shutdown.exe", "/s", "/t", "0"]

    if system == "Linux":
        return ["sudo", "/usr/bin/shutdown", "now"]

    if system == "Darwin":
        return ["sudo", "/sbin/shutdown", "now"]

    raise RuntimeError("Unsupported OS: {}".format(system))


def run_shutdown(dry_run):
    command = shutdown_command()
    print("Running: {}".format(" ".join(command)), flush=True)

    if dry_run:
        return

    subprocess.run(command, check=False)


def listen(port, dry_run):
    print("Listening on {} at {} baud".format(port, BAUD_RATE), flush=True)
    print("Host OS: {}".format(platform.system()), flush=True)

    with serial.Serial(port, BAUD_RATE, timeout=1) as ser:
        while True:
            raw = ser.readline()
            if not raw:
                continue

            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            print(line, flush=True)

            if line == TRIGGER:
                run_shutdown(dry_run)
                time.sleep(2)
            elif line in OLD_PICO_COMMANDS:
                print(
                    "Ignored old Pico command. Upload the updated main.py so Pause sends {}.".format(
                        TRIGGER
                    ),
                    flush=True,
                )


def wait_for_port(requested_port):
    while True:
        port = requested_port or find_port()
        if port:
            return port

        print(
            "Waiting for Pico serial port. Available ports: {}".format(
                available_ports_text()
            ),
            flush=True,
        )
        time.sleep(RETRY_SECONDS)


def run_forever(requested_port, dry_run, wait):
    while True:
        port = wait_for_port(requested_port) if wait else requested_port or find_port()

        if not port:
            print("Could not auto-detect Pico serial port.", file=sys.stderr)
            print("Available ports: {}".format(available_ports_text()), file=sys.stderr)
            print("Run again with --port PORT, or omit --no-wait.", file=sys.stderr)
            return 1

        try:
            listen(port, dry_run)
        except KeyboardInterrupt:
            print("Stopped.", flush=True)
            return 0
        except (OSError, SerialException) as exc:
            if not wait:
                raise

            print("Serial connection lost: {}".format(exc), flush=True)
            print("Reconnecting in {} seconds...".format(RETRY_SECONDS), flush=True)
            time.sleep(RETRY_SECONDS)


def main():
    parser = argparse.ArgumentParser(
        description="Listen for a Raspberry Pi Pico IR shutdown trigger."
    )
    parser.add_argument(
        "--port",
        help="Serial port, for example COM3 on Windows or /dev/ttyACM0 on Linux.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the shutdown command without running it.",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Exit if the Pico is not connected instead of waiting/reconnecting.",
    )
    args = parser.parse_args()

    return run_forever(args.port, args.dry_run, not args.no_wait)


if __name__ == "__main__":
    raise SystemExit(main())
