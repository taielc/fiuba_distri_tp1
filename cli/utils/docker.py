from . import paths
from subprocess import run, CalledProcessError, PIPE


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
