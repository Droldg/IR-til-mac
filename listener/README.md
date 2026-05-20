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

On Arch/Linux the script runs:

```bash
sudo /usr/bin/shutdown now
```

That command needs a matching `sudoers` rule if you want shutdown without a password.
