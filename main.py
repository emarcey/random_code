import ast
import concurrent.futures
from io import StringIO
import os
from prettytable import PrettyTable
from random import choices, randint
import signal
import sys
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


def render_row(t, name, vals):
    t.add_row([name] + [f"{round(x, 2):,}" for x in [min(vals), max(vals), round(sum(vals) / len(vals), 2), sum(vals)]])


def render(target_func, min_size, max_size, n, results):
    t0 = PrettyTable(align="l")
    t0.field_names = ["Target Func", "Min Result Size", "Max Result Size", "Num Results"]
    t0.add_row([target_func.__name__, min_size, max_size, n])

    t1 = PrettyTable(align="r")
    t1.field_names = ["Metric", "Min", "Max", "Avg", "Total"]
    t1.align["Metric"] = "l"
    render_row(t1, "Duration (s)", [r[2] for r in results])
    render_row(t1, "Code Samples Generated", [r[3] for r in results])
    render_row(t1, "Code Sample Length", [len(r[1]) for r in results])

    t2 = PrettyTable(align="l")
    t2.field_names = ["Code Samples"]
    t2.add_rows([[repr(r[1])] for r in results])
    print(f"{t0}\n{t1}\n{t2}")


def process(target_func: Callable, min_size=3, max_size=100, n=10):
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = []
        futures = [executor.submit(main, target_func, min_size, max_size) for i in range(min(n, os.cpu_count()))]
        try:
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        except Exception as e:
            raise e

    render(target_func, min_size, max_size, n, results)
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


def is_object(x):
    try:
        val = ast.literal_eval(x)
        return isinstance(val, object)
    except:
        return None


if __name__ == "__main__":
    process(is_true, 8, 20, 5)
