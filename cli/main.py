"""Main scripts"""

import click
from subprocess import run
from os import environ
from .utils import docker, BUILDABLE_PACKAGES, PACKAGES, paths


def _run_on_package(package: str, command: str):
    print(f"{package}> {command}")
    environ["PACKAGE"] = package
    run(command, shell=True, cwd=paths.TP1 / package)


@click.group()
def tp1():
    pass


@tp1.group("docker")
def docker_():
    pass


@docker_.command("build")
@click.argument(
    "package",
    type=click.Choice(BUILDABLE_PACKAGES),
    required=False,
)
def docker_build(package: str):
    print(f"Creating image for {package}")
    if package is None:
        for package in BUILDABLE_PACKAGES:
            _run_on_package(package, docker.build_cmd(package))
    else:
        _run_on_package(package, docker.build_cmd(package))


@tp1.command(
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    ),
)
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
)
def for_each_do(args: tuple[str]):
    if not args:
        raise click.UsageError("No arguments provided")
    command = " ".join(args)
    for package in PACKAGES:
        _run_on_package(package, command)


if __name__ == "__main__":
    tp1()
