import sys
from os import environ, getcwd
from subprocess import run, CalledProcessError

from . import paths

BUILDABLE_PACKAGES = [
    "server",
    "worker",
    "client",
]

PACKAGES = [
    *BUILDABLE_PACKAGES,
    "middleware",
    "lib",
]


def run_on_package(package: str, command: str, envs: dict = {}):
    cwd = getcwd()
    wd = paths.TP1 / package
    print(f"{wd.relative_to(cwd)}$ {command}")
    environ["PACKAGE"] = package
    environ.update(envs)
    current_env = environ.copy()
    current_env.pop("VIRTUAL_ENV", None)
    try:
        run(
            command,
            cwd=wd,
            shell=True,
            check=True,
            env=current_env,
        )
    except CalledProcessError as e:
        print(e)
        sys.exit(1)
