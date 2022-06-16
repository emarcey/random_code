import signal
import ast
import concurrent.futures
from io import StringIO
from json import loads
import os
from random import choices, randint
import sys
import threading
import time
from typing import Callable, Tuple
import warnings

chars = ["\t", "\n", "\r", " ", "!", '"'] + [chr(i) for i in range(36, 127)]


class Capturing(list):
    # https://stackoverflow.com/a/16571630
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def gen_code(min_size=3, max_size=100) -> str:
    return "".join(choices(chars, k=randint(min_size, max_size)))


def my_exec(code):
    try:
        with Capturing() as output, warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=SyntaxWarning)
            exec(f"print({code})")
        return "".join(output)
    except Exception as e:
        return None


def main(target_func: Callable, min_size=3, max_size=100) -> Tuple[bool, str, float, int]:
    start_time = time.time()
    i = 0
    while True:
        my_code = gen_code(min_size, max_size)
        if target_func(my_exec(my_code)):
            return True, my_code, round(time.time() - start_time, 2), i
        if i > 0 and i % 1_000_000 == 0:
            print(f"Trial {i:,} {my_code}")
        i += 1

    return False, "", round(time.time() - start_time, 2), i


def process(target_func: Callable, min_size=3, max_size=100, n=10):
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = []
        futures = [executor.submit(main, target_func, min_size, max_size) for i in range(min(n, os.cpu_count()))]
        [completed, incomplete] = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
        try:
            for future in completed:
                results.append(future.result())
            for p in executor._processes:
                os.kill(p, signal.SIGTERM)
        except Exception as e:
            raise e

    num_results = len(results)
    print(f"Num Results: {num_results}")
    print(f"Total Duration (s): {round(time.time() - start_time, 2):,}")
    print(f"Number of Tries: {round(float(sum([r[3] for r in results]))/num_results, 2):,}")
    print(f"Approx Total Number of Tries: {(round(float(sum([r[3] for r in results]))/num_results, 2)) * n:,}")
    print(f"Code Samples: {[r[1] for r in results]}")
    return results


def is_string(x):
    return isinstance(x, str)


def is_true(x):
    try:
        val = ast.literal_eval(x)
        return isinstance(val, bool) and val
    except:
        return None


def is_nonempty_dict(x):
    try:
        val = ast.literal_eval(x)
        return isinstance(val, dict) and len(val) > 0
    except:
        return None


def is_dict(x):
    try:
        val = ast.literal_eval(x)
        return isinstance(val, dict)
    except:
        return None


if __name__ == "__main__":
    process(is_nonempty_dict, 8, 20, 5)
