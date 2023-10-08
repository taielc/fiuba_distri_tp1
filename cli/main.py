"""Main scripts"""

from os import environ
from subprocess import run
import click


from .utils import (
    docker,
    BUILDABLE_PACKAGES,
    RUNNABLE_PACKAGES,
    PACKAGES,
    paths,
)


def _run_on_package(package: str, command: str, chdir: bool = True):
    wd = paths.TP1 / package
    print(f"{wd}$ {command}")
    environ["PACKAGE"] = package
    current_env = environ.copy()
    current_env.pop("VIRTUAL_ENV", None)
    if chdir:
        command = f"cd {wd} && {command}"
    run(
        command,
        cwd=wd,
        shell=True,
        check=True,
        start_new_session=True,
        env=current_env,
    )


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
    packages = BUILDABLE_PACKAGES
    if package is not None:
        packages = [package]
    for package in packages:
        _run_on_package(
            package,
            docker.build_cmd(package),
            chdir=False,
        )


def _docker_compose(exclude: tuple[str], args: tuple[str]):
    command = " ".join(args)
    if len(exclude) != 0:
        packages = [p for p in RUNNABLE_PACKAGES if p not in exclude]
        command = command + " " + " ".join(packages)
    compose_path = paths.DOCKER / "docker-compose.yaml"
    full_command = f"docker-compose -f {compose_path} {command}"
    print(f"Running docker-compose:\n> {full_command}")
    run(
        full_command,
        cwd=paths.ROOT,
        shell=True,
        check=True,
        start_new_session=True,
    )

@docker_.command(
    "compose",
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    ),
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    type=click.Choice(RUNNABLE_PACKAGES),
)
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
)
def docker_compose(exclude: tuple[str], args: tuple[str]):
    _docker_compose(exclude, args)


@tp1.command(
    "dc",
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    ),
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    type=click.Choice(RUNNABLE_PACKAGES),
)
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
)
def dc(exclude: tuple[str], args: tuple[str]):
    _docker_compose(exclude, args)


@tp1.command(
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    ),
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    type=click.Choice(PACKAGES),
)
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
)
def for_each_do(exclude: tuple[str], args: tuple[str]):
    if not args:
        raise click.UsageError("No arguments provided")
    command = " ".join(args)
    for package in PACKAGES:
        if package in exclude:
            continue
        _run_on_package(package, command)


if __name__ == "__main__":
    tp1()
