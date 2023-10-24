from subprocess import run, CalledProcessError, PIPE

from . import paths


BASE_BUILD_COMMAND = f"""docker build \\
    -f {paths.DOCKER}/Dockerfile \\
    --build-arg include={{include}} \\
    --build-arg package={{package}} \\
    -t tp1-{{package}} \\
    {paths.ROOT}
"""

INCLUDES = {
    "client": "lib",
    "server": "middleware",
    "worker": "middleware",
}


def build_cmd(package: str):
    command = BASE_BUILD_COMMAND.format(
        package=package, include=INCLUDES[package]
    )
    return command


def is_running(container: str):
    try:
        run(
            ["docker", "inspect", container],
            check=True,
            shell=False,
            stdout=PIPE,
        )
        return True
    except CalledProcessError:
        return False


def compose(args: tuple[str], show_output: bool = False):
    command = " ".join(args)
    compose_path = paths.DOCKER / "docker-compose.yaml"
    full_command = f"docker-compose -f {compose_path} {command}"
    print(f"Running docker-compose {args[0]}")
    # supress output
    run(
        full_command,
        cwd=paths.ROOT,
        shell=True,
        check=True,
        start_new_session=False,
        stdout=None if show_output else PIPE,
    )
