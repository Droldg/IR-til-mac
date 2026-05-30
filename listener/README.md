# Pico IR shutdown listener

The Pico sends `SHUTDOWN` over USB serial when the Apple Remote `Pause` button is pressed.
This script listens for that message and runs the right shutdown command for the host OS.

Install dependency:

```bash
pip install -r requirements.txt
```

Test without shutting down:

```bash
python listener.py --dry-run
```

If the Pico port is not found automatically, pass it manually:

```bash
python listener.py --port COM3 --dry-run
python listener.py --port /dev/ttyACM0 --dry-run
```

Run for real:

```bash
python listener.py
```

The listener now waits for the Pico if it is not connected yet. That means you can
start it at login and plug the Pico in later.

Windows startup:

Run this once from PowerShell:

```powershell
.\install_startup_windows.ps1
```

This creates a Startup shortcut that runs `start_listener_windows.ps1` every time
you log in. The listener then waits until the Pico is plugged in.

You can also install it manually:

1. Press `Win+R`.
2. Run `shell:startup`.
3. Create a shortcut with this target, adjusted to your path:

```powershell
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\path\to\listener\start_listener_windows.ps1"
```

The PowerShell script writes output to `listener.log` in the listener folder.

Windows uninstall:

Run this once from PowerShell:

```powershell
.\uninstall_startup_windows.ps1
```

Linux startup:

Run this once:

```bash
python3 install_startup_linux.py
```

This creates and starts a systemd user service for the listener.

Linux uninstall:

```bash
python3 install_startup_linux.py --uninstall
```

The generated service looks like this:

```ini
[Unit]
Description=Pico IR shutdown listener

[Service]
ExecStart=/bin/sh -c 'cd /path/to/listener && exec /usr/bin/python3 /path/to/listener/listener.py'
Restart=always
RestartSec=2

[Install]
WantedBy=default.target
```

The script saves it as `~/.config/systemd/user/pico-ir-listener.service`, then
runs:

```bash
systemctl --user daemon-reload
systemctl --user enable --now pico-ir-listener.service
```

On Linux the listener runs:

```bash
sudo /usr/bin/shutdown now
```

That command needs a matching `sudoers` rule if you want shutdown without a password.
