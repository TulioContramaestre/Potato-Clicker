# Potato-Clicker

A tkinter auto-clicker for Windows.

## Download & run (end users)

1. Grab `PotatoClicker.exe` from the [latest release](../../releases).
2. Double-click it. No install, no Python needed.
3. First launch: Windows SmartScreen may show a blue "Windows protected your PC" dialog — click **More info** → **Run anyway**. This happens for unsigned indie software; the warning fades once the release accumulates downloads.
4. In the app: set delay, pick mouse button, press **Start** (or **Shift+P** to toggle — note the uppercase P is intentional, it prevents accidental lowercase `p` toggles while typing).

## Building from source (developers)

See [build.sh](build.sh). Requires Python 3.12 (python.org installer, not the Store build) on Windows, and Git Bash.

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
pip install pyinstaller nuitka ordered-set zstandard
bash build.sh
```

Output: `dist/PotatoClicker.exe` is the single-file build for distribution.
