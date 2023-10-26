from subprocess import run, CalledProcessError, PIPE
from time import sleep
import requests

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
    # check if 'is not running' to avoid exception
    try:
        run(
            "docker exec -it middleware bash -c 'rabbitmqctl stop_app'",
            cwd=ROOT,
            shell=True,
            check=True,
            stdout=PIPE,
            stderr=PIPE,
        )
    except CalledProcessError:
        pass


def wait_until_running():
    """Wait until rabbitmq is up by polling the management api."""
    url = "http://localhost:15672/api/healthchecks/node"
    auth = ("admin", "admin")
    print("Waiting for rabbitmq to start...", end="")
    while True:
        print(".", end="", flush=True)
        sleep(0.8)
        try:
            r = requests.get(url, auth=auth, timeout=10)
            r.raise_for_status()
            print("OK")
            break
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.HTTPError:
            pass
        except requests.exceptions.ReadTimeout:
            pass
