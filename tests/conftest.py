# import multiprocessing as mp
# import os
# import signal
# import time

# import pytest


# def wait_sigint(q: mp.Queue, pid):
#     try:
#         q.get(timeout=10)
#     except Exception:
#         print("Timeout")
#         os.kill(pid, signal.SIGINT)

#         time.sleep(30)
#         try:
#             os.kill(pid, 0)
#         except OSError:
#             pass
#         else:
#             os.kill(pid, signal.SIGKILL)


# @pytest.fixture(scope="function", autouse=True)
# def sigint_after_time():
#     start = time.perf_counter()
#     manager = mp.Manager()
#     q = manager.Queue()
#     p = mp.Process(target=wait_sigint, args=(q, os.getpid()))
#     p.start()
#     yield
#     q.put(1)
#     p.join()
#     end = time.perf_counter()
#     print("time: ", end - start)
