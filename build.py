"""Build the offline Windows x64 patcher from this repository."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onefile',
                '--windowed', '--name', 'XBOX-Crazy-Taxi-3-Kr-v1.0-Patcher',
                '--distpath', str(ROOT / 'dist'), '--workpath', str(ROOT / 'build'),
                '--specpath', str(ROOT / 'build'),
                '--add-data', str(ROOT / 'patches') + ';patches',
                '--add-data', str(ROOT / 'licenses') + ';licenses',
                '--add-binary', str(ROOT / 'vendor/xdelta3.exe') + ';vendor',
                str(ROOT / 'src/patcher.py')], check=True)
