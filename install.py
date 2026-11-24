import os
from pathlib import Path
import subprocess
import sys


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10 or newer is required.")

    project_dir = Path(__file__).resolve().parent
    venv_dir = project_dir / ".venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
    )

    if os.name == "nt":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"

    subprocess.run(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "-r",
            str(project_dir / "requirements.txt"),
        ],
        cwd=project_dir,
        check=True,
    )
    print("Setup complete. Activate the .venv environment before running the app.")


if __name__ == "__main__":
    main()
