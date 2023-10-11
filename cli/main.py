"""Main scripts"""

from os import environ
from subprocess import run
from time import sleep
import click


from .utils import (
    docker,
    BUILDABLE_PACKAGES,
    RUNNABLE_PACKAGES,
    PACKAGES,
    paths,
    render_template,
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


def _docker_compose(args: tuple[str]):
    command = " ".join(args)
    compose_path = paths.DOCKER / f"docker-compose.yaml"
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
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
)
def docker_compose(args: tuple[str]):
    _docker_compose(args)


@tp1.command(
    "dc",
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
def dc(args: tuple[str]):
    _docker_compose(args)


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


def _generate_docker_compose_dev(worker_counts: list[tuple[str, int]] = []):
    docker_compose_file = paths.DOCKER / "docker-compose.yaml"
    with docker_compose_file.open("w") as f:
        f.write(
            render_template(
                paths.DOCKER / "docker-compose-dev.yaml.j2",
                workers=worker_counts,
            )
        )
    print("Successfully built", docker_compose_file.relative_to(paths.ROOT))


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
def build(args: tuple[str]):
    worker_counts = [
        (args[i].lstrip("--").replace("-", "_"), int(args[i + 1]))
        for i in range(0, len(args), 2)
    ]
    _generate_docker_compose_dev(worker_counts)


@tp1.command()
def reset_middleware():
    run(
        "docker exec -it middleware bash -c "
        "'rabbitmqctl stop_app; "
        "rabbitmqctl reset; "
        "rabbitmqctl start_app'",
        cwd=paths.ROOT,
        shell=True,
        check=True,
        start_new_session=True,
    )


@tp1.command(
    "run",
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
def run_tp1(args: tuple[str]):
    """
    tp1 run --worker-a 2 --worker-b 2
    """
    worker_counts = [
        (args[i].lstrip("--").replace("-", "_"), int(args[i + 1]))
        for i in range(0, len(args), 2)
    ]
    _generate_docker_compose_dev(worker_counts)
    if not docker.is_running("middleware"):
        _docker_compose(("up", "-d", "middleware"))
        sleep(5)
    services = tuple(
        f"{worker}-{i}"
        for worker, count in worker_counts
        for i in range(1, count + 1)
    ) + ("client", "server")
    _docker_compose(("up", "-d") + services)
    print("Check logs with:")
    print(
        "docker compose -f docker/docker-compose.yaml logs -f "
        + " ".join(services)
    )
    with open(paths.ROOT / "cli/tmp/running_services.txt", "w") as f:
        f.write("\n".join(services))


def _stop(rm: bool):
    with open(paths.ROOT / "cli/tmp/running_services.txt") as f:
        services = f.read().splitlines()
    _docker_compose(("stop",) + tuple(services))
    print("Stopped services")
    if rm:
        _docker_compose(("rm", "-f") + tuple(services))
        print("Removed services")

@tp1.command()
@click.option(
    "--rm",
    is_flag=True,
    help="Remove containers after stopping",
)
def stop(rm: bool):
    _stop(rm)


@tp1.command()
@click.option(
    "--rm",
    is_flag=True,
    help="Remove containers after stopping",
)
def restart(rm: bool):
    _stop(rm)
    with open(paths.ROOT / "cli/tmp/running_services.txt") as f:
        services = f.read().splitlines()
    _docker_compose(("up", "-d") + tuple(services))


@tp1.command()
def down():
    run(
        "docker exec -it middleware bash -c " "'rabbitmqctl stop_app'",
        cwd=paths.ROOT,
        shell=True,
        check=True,
        start_new_session=True,
    )
    _docker_compose(("down", "-v", "--remove-orphans"))


if __name__ == "__main__":
    tp1()
