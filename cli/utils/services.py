from .template_parser import render_template
from . import paths
from . import docker

SERVICES_PATH = paths.ROOT / "cli/tmp/running_services.csv"


def _save_workers(services: list[tuple[str, int]]):
    with SERVICES_PATH.open("w") as f:
        f.write("\n".join(map(lambda s: f"{s[0]},{s[1]}", services)))


def get_services() -> list[tuple[str, int]]:
    with SERVICES_PATH.open() as f:
        return [
            f"{service}-{i}"
            for service, count in map(
                lambda s: s.split(","), f.read().splitlines()
            )
            for i in range(1, int(count) + 1)
        ] + ["server", "fastest_by_route", "price_by_route"]


def configure_docker_compose(worker_counts: list[tuple[str, int]] = None):
    if worker_counts is None:
        worker_counts = []
    docker_compose_file = paths.DOCKER / "docker-compose.yaml"
    with docker_compose_file.open("w") as f:
        f.write(
            render_template(
                paths.DOCKER / "docker-compose-dev.yaml.j2",
                workers=worker_counts,
            )
        )
    print("Successfully built", docker_compose_file.relative_to(paths.ROOT))
    _save_workers(worker_counts)


def stop_services(rm: bool):
    services = get_services()
    docker.compose(("stop",) + tuple(services))
    print("Stopped services")
    if rm:
        docker.compose(("rm", "--force") + tuple(services))
        print("Removed services")
