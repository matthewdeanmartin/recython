import io
import sys
import timeit
from decimal import ROUND_HALF_UP, Decimal
from unittest import mock

from recython.filesystem import run as filesystem_cython
from recython.scrape import run as scrape_cython

# Import your functions
from recython.tidy import run as tidy_cython
from recython_pure.filesystem import run as filesystem_pure
from recython_pure.scrape import run as scrape_pure
from recython_pure.tidy import run as tidy_pure

# from memory_profiler import memory_usage


REPEATS = 2000


def benchmark_function(func, *args, **kwargs):
    """
    Benchmark a given function in terms of time and memory.

    Args:
        func (Callable): The function to benchmark.
        *args: Variable length argument list for the function.
        **kwargs: Arbitrary keyword arguments for the function.

    Returns:
        tuple: Tuple containing (average time, memory usage)
    """
    captured_output = io.StringIO()
    sys.stdout = captured_output
    # Time benchmarking
    time_taken = timeit.timeit(lambda: func(*args, **kwargs), number=REPEATS)

    # Memory benchmarking
    mem_usage = (0, 0)  # memory_usage((func, args, kwargs), max_usage=True)

    # Restore the standard output to its original state
    sys.stdout = sys.__stdout__

    # Get the standard output contents
    captured_output.getvalue()
    captured_output.close()

    return time_taken, mem_usage[0]


def format_ratio(cython_time, pure_time):
    if cython_time < pure_time:
        ratio = (1 - Decimal(cython_time) / Decimal(pure_time)) * 100
        formatted_ratio = ratio.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"Ratio: {formatted_ratio}% faster"
    else:
        ratio = (1 - Decimal(pure_time) / Decimal(cython_time)) * 100
        formatted_ratio = ratio.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"Ratio: {formatted_ratio}% slower"


if __name__ == "__main__":
    print(f"Test will repeat {REPEATS} times")
    # Replace 'args' and 'kwargs' with actual arguments for your functions if any
    pairs = {
        "filesystem": (filesystem_cython, filesystem_pure),
        "tidy": (tidy_cython, tidy_pure),
        "scrape": (scrape_cython, scrape_pure),
    }

    for name, (cython, pure) in pairs.items():
        try:
            pure()
            print(f"Can run pure {name}")
        except Exception as e:
            print(f"Error in {name} pure: {e}")
            continue

        try:
            cython()
        except Exception as e:
            print(f"Error in {name} cython: {e}")
            continue
        with mock.patch("requests.get") as mock_get_patcher:
            mock_response = mock_get_patcher.return_value
            mock_response.raise_for_status.return_value = None
            mock_response.text = "<div class='body'>Test content</div>"

            cython_time, cython_memory = benchmark_function(cython)
            pure_time, pure_memory = benchmark_function(pure)
            print(f"Cython Function - Time: {round(cython_time, 5)} u-sec")
            print(f"Pure Python Function - Time: {round(pure_time,5)}u-sec")
            print(format_ratio(cython_time, pure_time))
