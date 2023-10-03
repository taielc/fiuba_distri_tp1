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
