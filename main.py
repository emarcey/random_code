import concurrent.futures
from random import choices, randint
import time
from typing import Tuple
import warnings

from io import StringIO
import sys

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
    except:
        return None


def main(target_value: any, min_size=3, max_size=100) -> Tuple[bool, str, float, int]:
    start_time = time.time()
    i = 0
    while True:
        my_code = gen_code(min_size, max_size)
        if str(my_exec(my_code)) == str(target_value):
            return True, my_code, round(time.time() - start_time, 2), i
        i += 1

    return False, "", round(time.time() - start_time, 2)


def process(target_value: any, min_size=3, max_size=100, n=10):
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = []
        futures = [executor.submit(main, target_value, min_size, max_size) for i in range(n)]
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
                print("Finished!")
            except Exception as e:
                raise e

    print(f"Num Results: {n}")
    print(f"Total Duration (s): {round(time.time() - start_time, 2):,}")
    print(f"Avg Duration (s): {round(float(sum([r[2] for r in results]))/n, 2):,}")
    print(f"Avg Number of Tries: {round(float(sum([r[3] for r in results]))/n, 2):,}")
    print(f"Code Samples: {[r[1] for r in results]}")
    return results


if __name__ == "__main__":
    process(True, 8, 20, 10)
