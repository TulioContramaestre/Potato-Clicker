#!/usr/bin/env bash
# Run from project folder with venv activated: source .venv/Scripts/activate
set -e
rm -rf build dist PotatoClicker.build PotatoClicker.dist PotatoClicker.onefile-build
mkdir -p dist

# --- Nuitka --onefile: the artifact users download ---
python -m nuitka \
    --onefile \
    --windows-console-mode=disable \
    --enable-plugin=tk-inter \
    --windows-icon-from-ico=icon.ico \
    --company-name=PotatoClicker \
    --product-name=PotatoClicker \
    --file-version=1.0.0.0 \
    --product-version=1.0.0.0 \
    --file-description="PotatoClicker auto-clicker" \
    --output-filename=PotatoClicker.exe \
    --output-dir=dist \
    PotatoClicker.py

# --- PyInstaller --onefile: for VirusTotal comparison only, NOT for distribution ---
pyinstaller \
    --noconfirm --windowed --onefile --noupx \
    --name PotatoClicker-pyinstaller \
    --version-file version_info.txt \
    --icon icon.ico \
    PotatoClicker.py

echo ""
echo "SHIP THIS: dist/PotatoClicker.exe  (Nuitka onefile)"
echo "COMPARE ONLY (do not distribute): dist/PotatoClicker-pyinstaller.exe"
