from os import environ
from subprocess import run, CalledProcessError

from . import paths

BUILDABLE_PACKAGES = [
    "server",
    "worker",
]

RUNNABLE_PACKAGES = [
    *BUILDABLE_PACKAGES,
    "middleware",
]

PACKAGES = [
    *RUNNABLE_PACKAGES,
    "lib",
]


def run_on_package(
    package: str, command: str, envs: dict = {}
):
    wd = paths.TP1 / package
    print(f"{wd}$ {command}")
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
        exit(1)
