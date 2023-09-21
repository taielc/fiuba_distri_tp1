"""Main scripts"""

import click
from .utils import docker, BUILDABLE_PACKAGES, PACKAGES, poetry


@click.group()
def tp1():
    pass


@tp1.command()
@click.argument(
    "package",
    type=click.Choice(BUILDABLE_PACKAGES),
    required=False,
)
def build_image(package: str):
    print(f"Creating image for {package}")
    if package is None:
        for image in BUILDABLE_PACKAGES:
            docker.build(image)
    else:
        docker.build(package)


@tp1.command(
    "poetry",
    context_settings=dict(
        allow_extra_args=True,
    ),
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def poetry_(args: tuple[str]):
    if not args:
        raise click.UsageError("No arguments provided")
    package = None
    if args[0] in PACKAGES:
        package = args[0]
        args = args[1:]
    command = " ".join(args)
    if package is None:
        for package in PACKAGES:
            poetry.run_command(package, command)
    else:
        poetry.run_command(package, command)
    


if __name__ == "__main__":
    tp1()
