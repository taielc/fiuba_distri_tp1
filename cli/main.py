"""Main scripts"""

from subprocess import run
from time import sleep
import click


from .utils import (
    docker,
    BUILDABLE_PACKAGES,
    PACKAGES,
    paths,
    run_on_package,
    configure_docker_compose,
    get_services,
    stop_services,
    middleware,
)


@click.group()
def tp1():
    pass


@tp1.command("build")
@click.argument(
    "package",
    type=click.Choice(BUILDABLE_PACKAGES),
    required=False,
)
def build_(package: str):
    packages = BUILDABLE_PACKAGES
    if package is not None:
        packages = [package]
    print(f"Creating image for {package}")
    for package in packages:
        run_on_package(
            package,
            docker.build_cmd(package),
        )


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
        run_on_package(package, command)


@tp1.command(
    "configure",
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
def configure(args: tuple[str]):
    worker_counts = [
        (args[i].lstrip("--").replace("-", "_"), int(args[i + 1]))
        for i in range(0, len(args), 2)
    ]
    configure_docker_compose(worker_counts)


@tp1.command("reset-middleware")
def reset_middleware_():
    middleware.reset()


@tp1.command(
    "run",
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    ),
)
@click.option(
    "--build",
    is_flag=True,
    help="Build docker images",
)
@click.option(
    "--restart",
    is_flag=True,
    help="Stop and restart services",
    default=False,
)
@click.option(
    "--no-remove",
    is_flag=True,
    help="Don't remove containers after stopping (only if --restart)",
    default=False,
)
@click.option(
    "--reset-middleware",
    "-r",
    is_flag=True,
    help="Reset middleware",
)
@click.option(
    "--logs",
    "-l",
    is_flag=True,
    help="Follow logs after running",
    default=False,
)
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
)
def run_tp(
    build: bool,
    restart: bool,
    no_remove: bool,
    reset_middleware: bool,
    logs: bool,
    args: tuple[str],
):
    """
    tp1 run --worker-a 2 --worker-b 2
    """
    if args:
        worker_counts = [
            (args[i].lstrip("--").replace("-", "_"), int(args[i + 1]))
            for i in range(0, len(args), 2)
        ]
        configure_docker_compose(worker_counts)
    if not docker.is_running("middleware"):
        docker.compose(("up", "-d", "middleware"))
        sleep(5)
    if restart:
        stop_services((not no_remove))
    if reset_middleware:
        middleware.reset()
    services = get_services()
    docker.compose(
        ["up", "-d", "--remove-orphans", "--build" if build else ""] + services
    )
    if logs:
        docker.compose(("logs", "-f") + tuple(services))
    else:
        print("Check logs with:")
        print(
            "docker compose -f docker/docker-compose.yaml logs -f "
            + " ".join(services)
        )


@tp1.command()
def logs():
    docker.compose(("logs", "-f") + tuple(get_services()))


@tp1.command()
@click.option(
    "--rm",
    is_flag=True,
    help="Remove containers after stopping",
)
def stop(rm: bool):
    stop_services(rm)


@tp1.command()
def down():
    run(
        "docker exec -it middleware bash -c 'rabbitmqctl stop_app'",
        cwd=paths.ROOT,
        shell=True,
        check=True,
        start_new_session=True,
    )
    docker.compose(("down", "-v", "--remove-orphans"))


@tp1.command()
@click.option(
    "--build",
    is_flag=True,
    help="Build docker image, if local: run poetry install",
)
@click.option(
    "--local",
    "-l",
    is_flag=True,
    help="Run locally instead of dockerized",
)
def client(local: bool, build: bool):
    if local:
        if build:
            run_on_package("client", "poetry install")
        run_on_package(
            "client", "poetry run main", envs={"SERVER_HOST": "localhost"}
        )
        return
    if build:
        run_on_package("client", docker.build_cmd("client"))
    cmd = [
        "docker run -it --rm --network=docker_default",
        f"--volume {paths.ROOT}/.data:/.data:rw",
        f"--volume {paths.TP1}/lib/src/:/tp1/lib/src/:rw",
        f"--volume {paths.TP1}/client/src/:/tp1/client/src/:rw",
        "tp1-client",
    ]
    print(" \\\n  ".join(cmd))
    run(
        " \\\n  ".join(cmd),
        check=True,
        shell=True,
    )


if __name__ == "__main__":
    tp1()
