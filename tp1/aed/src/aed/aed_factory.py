from multiprocessing import Process

from aed import AED

def main():
    aed = AED()
    Process(target=aed.run_healthcheck).start()

