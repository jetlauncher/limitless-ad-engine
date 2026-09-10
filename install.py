"""Install the local app into its own virtual environment (Python 3.11+)."""
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent

def main():
    if sys.version_info < (3, 11):
        print('Please install Python 3.11 or newer.'); return 1
    env = ROOT / '.venv'
    python = env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    try:
        if not python.exists():
            if env.exists():
                raise ValueError('.venv exists but has no Python. Choose a fresh clone or repair the environment.')
            print('Creating a local Python environment...', flush=True)
            venv.EnvBuilder(with_pip=True).create(env)
        subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(ROOT / 'requirements.txt')], check=True)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print('Installation did not finish:', exc)
        print('On Linux, install your distribution\'s python3-venv package if venv is unavailable.')
        return 1
    print('\nInstalled. Run: python3 start.py\nWindows: py start.py')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
