from subprocess import run, PIPE
from . import paths


def _create_poetry_base_image_if_not_exists():
    command = "docker images | grep tp1-poetry-base"
    result = run(command, shell=True, stdout=PIPE)
    # get the exit code
    if result.returncode != 0:
        print("Base image not found, building...")
        command = "docker build -t tp1-poetry-base -f poetry_base.Dockerfile ."
        run(command, shell=True, cwd=paths.SCRIPTS)


def build(package: str):
    _create_poetry_base_image_if_not_exists()
    command = f"docker build -t {package} -f {package}/Dockerfile ."
    print(command)
    run(command, shell=True, cwd=paths.ROOT)
