import multiprocessing as mp
import os
import signal

import pytest


def wait_sigint(q: mp.Queue, pid):
    try:
        q.get(timeout=60)
    except Exception:
        print("Timeout")
        os.kill(pid, signal.SIGINT)
        import time

        time.sleep(30)
        try:
            os.kill(pid, 0)
        except OSError:
            pass
        else:
            os.kill(pid, signal.SIGKILL)


@pytest.fixture(scope="session", autouse=True)
def sigint_after_time():
    manager = mp.Manager()
    q = manager.Queue()
    p = mp.Process(target=wait_sigint, args=(q, os.getpid()))
    p.start()
    yield
    q.put(1)
    p.join()
