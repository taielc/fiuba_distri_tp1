from subprocess import run

from .paths import ROOT


def reset():
    run(
        "docker exec -it middleware bash -c "
        "'rabbitmqctl stop_app; "
        "rabbitmqctl reset; "
        "rabbitmqctl start_app'",
        cwd=ROOT,
        shell=True,
        check=True,
        start_new_session=True,
    )

def stop():
    run(
        "docker exec -it middleware bash -c 'rabbitmqctl stop_app'",
        cwd=ROOT,
        shell=True,
        check=True,
        start_new_session=True,
    )
