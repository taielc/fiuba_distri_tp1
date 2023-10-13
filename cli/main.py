"""Main scripts"""

from os import environ
from subprocess import run, CalledProcessError
from time import sleep
import click


from .utils import (
    docker,
    BUILDABLE_PACKAGES,
    PACKAGES,
    paths,
    render_template,
)


def _run_on_package(
    package: str, command: str, chdir: bool = True, envs: dict = {}
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
    "build",
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
def build_(args: tuple[str]):
    worker_counts = [
        (args[i].lstrip("--").replace("-", "_"), int(args[i + 1]))
        for i in range(0, len(args), 2)
    ]
    _generate_docker_compose_dev(worker_counts)


def _reset_middleware():
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


@tp1.command("reset-middleware")
def reset_middleware_():
    _reset_middleware()


def _save_workers(services: list[tuple[str, int]]):
    with open(paths.ROOT / "cli/tmp/running_services.csv", "w") as f:
        f.write("\n".join(map(lambda s: f"{s[0]},{s[1]}", services)))


def _get_running_workers() -> list[tuple[str, int]]:
    with open(paths.ROOT / "cli/tmp/running_services.csv") as f:
        return [
            f"{service}-{i}"
            for service, count in map(
                lambda s: s.split(","), f.read().splitlines()
            )
            for i in range(1, int(count) + 1)
        ]


def _get_worker_counts() -> list[tuple[str, int]]:
    with open(paths.ROOT / "cli/tmp/running_services.csv") as f:
        return [
            (service, int(count))
            for service, count in map(
                lambda s: s.split(","), f.read().splitlines()
            )
        ]


QUERY_DEFAULTS = [
    ["base_filter"],  # [0] base
    ["filter_by_stops"],
    ["dist_calculator"],
    ["filter_by_stops", "aggregate_by_route", "fastest_by_route"],
    ["general_avg_price", "filter_by_price", "price_by_route"],
]
FILTER_DEFAULTS = {
    # 0
    "base_filter": 1,
    # 1
    "filter_by_stops": 1,  # & 3
    # 2
    "dist_calculator": 1,
    # 3
    "aggregate_by_route": 1,
    "fastest_by_route": 1,
    # 4
    "general_avg_price": 1,
    "filter_by_price": 1,
    "price_by_route": 1,
}


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
    "--query",
    "-q",
    multiple=True,
    type=click.Choice(list(map(str, range(1, 5)))),
    help="Queries to run (--query 1 -q 2)",
)
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
)
def run_tp1(build: bool, query: tuple[str], args: tuple[str]):
    """
    tp1 run --worker-a 2 --worker-b 2
    """
    if query:
        queries = ("0",) + query
        workers = set(
            worker for query in queries for worker in QUERY_DEFAULTS[int(query)]
        )
        worker_counts = [
            (worker, FILTER_DEFAULTS[worker]) for worker in workers
        ]
    else:
        worker_counts = [
            (args[i].lstrip("--").replace("-", "_"), int(args[i + 1]))
            for i in range(0, len(args), 2)
        ]
    _generate_docker_compose_dev(worker_counts)
    if not docker.is_running("middleware"):
        _docker_compose(("up", "-d", "middleware"))
        sleep(5)
    services = [
        f"{worker}-{i}"
        for worker, count in worker_counts
        for i in range(1, count + 1)
    ] + ["server"]
    _docker_compose(
        ["up", "-d", "--remove-orphans", "--build" if build else ""] + services
    )
    print("Check logs with:")
    print(
        "docker compose -f docker/docker-compose.yaml logs -f "
        + " ".join(services)
    )
    _save_workers(worker_counts)


def _stop(rm: bool):
    services = _get_running_workers() + ["server"]
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
@click.option(
    "--no-rebuild",
    is_flag=True,
    help="Rebuild docker compose",
)
@click.option(
    "--reset-middleware",
    "-r",
    is_flag=True,
    help="Reset middleware",
)
def restart(rm: bool, no_rebuild: bool, reset_middleware: bool):
    _stop(rm)
    if reset_middleware:
        _reset_middleware()
    if not no_rebuild:
        worker_counts = _get_worker_counts()
        _generate_docker_compose_dev(worker_counts)
    services = _get_running_workers() + ["server"]
    _docker_compose(("up", "-d", "--remove-orphans") + tuple(services))


@tp1.command()
def down():
    run(
        "docker exec -it middleware bash -c 'rabbitmqctl stop_app'",
        cwd=paths.ROOT,
        shell=True,
        check=True,
        start_new_session=True,
    )
    _docker_compose(("down", "-v", "--remove-orphans"))


@tp1.command()
@click.option(
    "--build",
    is_flag=True,
    help="Build docker image",
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
            _run_on_package("client", "poetry install")
        _run_on_package(
            "client", "poetry run main", envs={"SERVER_HOST": "localhost"}
        )
        return
    if build:
        _run_on_package("client", docker.build_cmd("client"), chdir=False)
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
