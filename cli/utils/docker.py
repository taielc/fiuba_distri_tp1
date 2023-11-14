from subprocess import run, PIPE
from os import getcwd

from . import paths


BASE_BUILD_COMMAND = """docker build \
-f {docker_path}/Dockerfile \
--build-arg include={include} \
--build-arg package={package} \
-t tp1-{package} \
{root_path}
"""

INCLUDES = {
    "client": "lib",
    "aed": "lib",
    "server": "middleware",
    "worker": "middleware",
}


def build(package: str):
    cwd = getcwd()
    command = BASE_BUILD_COMMAND.format(
        package=package,
        include=INCLUDES[package],
        docker_path=paths.DOCKER.relative_to(cwd),
        root_path=paths.ROOT.relative_to(cwd),
    )
    print(f"$ docker build {package}")
    run(command, cwd=cwd, shell=True, check=True)


def is_running(container: str):
    result = compose(
        ("ps", "-q", container), capture_output=True, show_output=True
    )
    return bool(result.stdout)


def compose(
    args: tuple[str], show_output: bool = False, capture_output: bool = False
):
    command = " ".join(args)
    compose_path = paths.DOCKER / "docker-compose.yaml"
    full_command = f"docker-compose -f {compose_path} {command}"
    print(
        f"$ docker-compose {args[0]} "
        + " ".join([arg for arg in args[1:] if arg in ("server", "middleware")])
    )
    # supress output
    return run(
        full_command,
        cwd=paths.ROOT,
        shell=True,
        check=True,
        start_new_session=False,
        stdout=None if show_output else PIPE,
        stderr=None if show_output else PIPE,
        capture_output=capture_output,
    )
