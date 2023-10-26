"""Main scripts"""

from os import getcwd
from subprocess import run
from datetime import datetime
import click


from .utils import (
    docker,
    BUILDABLE_PACKAGES,
    PACKAGES,
    NON_SINGLE_WORKERS,
    SINGLE_WORKERS,
    paths,
    run_on_package,
    configure_docker_compose,
    get_services,
    stop_services,
    middleware,
)


@click.group()
def tp():
    pass


@tp.command("build")
@click.argument(
    "package", type=click.Choice(BUILDABLE_PACKAGES), required=False
)
def build_(package: str):
    packages = BUILDABLE_PACKAGES
    if package is not None:
        packages = [package]
    print(f"Creating image for {package}")
    for package in packages:
        docker.build(package),


@tp.command(
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    )
)
@click.option("--exclude", "-e", multiple=True, type=click.Choice(PACKAGES))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def for_each_do(exclude: tuple[str], args: tuple[str]):
    if not args:
        raise click.UsageError("No arguments provided")
    command = " ".join(args)
    for package in PACKAGES:
        if package in exclude:
            continue
        run_on_package(package, command)


def _configure_cmd(**kwargs):
    worker_counts = [
        (worker, count)
        for worker, count in kwargs.items()
        if worker in NON_SINGLE_WORKERS
    ]
    configure_docker_compose(worker_counts)


def _validate_greater_than_zero(ctx, param, value):
    if value <= 0:
        raise click.BadParameter("Must be greater than 0")
    return value


_configure = _configure_cmd
for worker, default in NON_SINGLE_WORKERS.items():
    _configure = click.option(
        f"--{worker.replace('_', '-')}",
        type=int,
        callback=_validate_greater_than_zero,
        default=default,
        show_default=True,
    )(_configure)

configure = tp.command(
    "configure",
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    ),
    help=(
        "Configure number of replicas for each worker"
        "\n\tNote: " + ", ".join(SINGLE_WORKERS) + " cannot be replicated"
    ),
)(_configure)


@tp.command("reset-middleware")
def reset_middleware_():
    middleware.reset()


@tp.command("run")
@click.option("--build", is_flag=True, help="Build docker images")
@click.option(
    "--restart", is_flag=True, help="Stop and restart services", default=False
)
@click.option(
    "--no-remove",
    is_flag=True,
    help="Don't remove containers after stopping (only if --restart)",
    default=False,
)
@click.option("--reset-middleware", "-r", is_flag=True, help="Reset middleware")
@click.option(
    "--detach",
    "-d",
    is_flag=True,
    help="Detach after running",
    default=False,
)
def run_tp(
    build: bool,
    restart: bool,
    no_remove: bool,
    reset_middleware: bool,
    detach: bool,
):
    print("Checking if middleware is running:")
    if not docker.is_running("middleware"):
        reset_middleware = False
        print("Middleware is not running, starting:")
        docker.compose(("up", "-d", "middleware"))
        middleware.wait_until_running()
    if restart:
        print("Restart set, stopping services:")
        stop_services((not no_remove))
    if reset_middleware:
        print("Resetting middleware:")
        middleware.reset()
    services = get_services()
    docker.compose(
        [
            "up",
            "-d" if detach else "",
            "--remove-orphans",
            "--build" if build else "",
        ]
        + services,
        show_output=not detach,
    )
    if detach:
        print("Check logs with:")
        print(
            "docker compose -f docker/docker-compose.yaml logs -f "
            + " ".join(services)
        )


@tp.command(
    "logs",
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    ),
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def logs_(args: tuple[str]):
    services = get_services()
    if any(arg in services for arg in args):
        services = []
    docker.compose(
        ("logs",) + args + tuple(services),
        show_output=True,
    )


@tp.command()
@click.option("--rm", is_flag=True, help="Remove containers after stopping")
@click.option("-m", is_flag=True, help="Stop middleware", default=False)
def stop(rm: bool, m: bool):
    if m:
        middleware.stop()
    stop_services(rm, middleware=m)


@tp.command()
def down():
    run(
        "docker exec -it middleware bash -c 'rabbitmqctl stop_app'",
        cwd=paths.ROOT,
        shell=True,
        check=True,
        start_new_session=True,
    )
    docker.compose(("down", "-v", "--remove-orphans"))


@tp.command()
@click.option(
    "--build",
    is_flag=True,
    help="Build docker image, if local: run poetry install",
)
@click.option(
    "--local", "-l", is_flag=True, help="Run locally instead of dockerized"
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
        docker.build("client")
    cwd = getcwd()
    cmd = [
        "docker run -it --rm --network=docker_default",
        f"--volume ./{paths.ROOT.relative_to(cwd)}/.data:/.data:rw",
        f"--volume ./{paths.TP1.relative_to(cwd)}/lib/src/:/tp1/lib/src/:rw",
        f"--volume ./{paths.TP1.relative_to(cwd)}/client/src/:/tp1/client/src/:rw",
        "tp1-client",
    ]
    print("$ ", " \\\n  ".join(cmd))
    run(" \\\n  ".join(cmd), check=True, shell=True)


if __name__ == "__main__":
    tp()
