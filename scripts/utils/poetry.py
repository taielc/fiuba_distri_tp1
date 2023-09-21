from subprocess import run, PIPE
from . import paths


def run_command(package: str, command: str):
    print(f"Running {command} for {package}")
    run("poetry " + command, shell=True, cwd=paths.ROOT / package)
