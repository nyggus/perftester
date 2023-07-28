"""A lightweight module for simple performance testing in Python.

The singleton Config class is used in all testing in the same session; its
instance is created during import and can be used by all functions.

Do note that unlike timeit functions, perftester works with times of a single
call of a function. That way, the user can define tests without worrying of
different settings: while the "number" argument in timeit functions affects
the results, it does not so in perftester.

Remember that all lambda functions are stored as anonymous functions,
without a name. Hence it's better to avoid using lambdas in perftester.

WARNING: Unlike memory_profiler.memory_usage(), which reports memory in MiB,
perftester provides data in MB. That way, the data from 
memory_profiler.memory_usage() and pympler.asizeof.asizeof() are provided in
the same units. If you want to recalculate the data to MiB, you can divide the
memory by perftester.MiB_TO_MB_FACTOR.

WARNING: Calculating memory can take quite some time when the 

For the sake of pretty-printing the benchmarks, perftester comes with a pp
function, which rounds all numbers to four significant digits and prints
the object using pprint.pprint:
>>> import perftester as pt
>>> pt.pp([2.1212, 2.93135])
[2.121, 2.931]

You can change this behavior, however:
>>> pt.config.digits_for_printing = 2
>>> pt.pp([2.1212, 2.93135])
[2.1, 2.9]

Let's return to previous settings:
>>> pt.config.digits_for_printing = 4
"""
import warnings
from pympler.asizeof import asizeof
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    STARTING_MEMORY = asizeof(all=True)

import builtins
import copy
import inspect
import gc
import os
import rounder
import sys
import timeit

from collections import namedtuple
from collections.abc import Callable
from easycheck import (
    check_argument,
    check_if,
    check_if_not,
    check_type,
    check_if_paths_exist,
    assert_instance,  # required for doctests
)
from functools import wraps
from memory_profiler import memory_usage
from pathlib import Path
from pprint import pprint
from statistics import mean


MiB_TO_MB_FACTOR = 1.048576


class IncorrectUseOfMEMLOGSError(Exception):
    """MEMLOGS was used incorrectly."""


class CLIPathError(Exception):
    """Exception class to be used for the CLI perftester app."""


class LogFilePathError(Exception):
    """Incorrect path provided for a log file."""


class LackingLimitsError(Exception):
    """No limits has been set for test."""


class IncorrectArgumentError(Exception):
    """Function arguments are incorrect."""


class TimeTestError(Exception):
    """The time test has not passed."""


class MemoryTestError(Exception):
    """The memory usage test has not passed."""


class FunctionError(Exception):
    """The tested code has thrown an error."""


# Configuration


class Config:
    """Default configuration for testing.

    It is a singleton whose instance is created once, during import
    of the perftester module.
    """

    config_file = Path("config_perftester.py")
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Attributes:
            defaults: a dict of dicts; defaults["time"] provide number and repeat
                to be passed to timeit.repeat; defaults["memory"] provide repeat,
                and the memory profiler will run that many times
            settings: a dict with values having the same structure as defaults;
                keys of the dict are functions; if the user does not change them,
                defaults are used
            time_benchmark: execution time of the in-built benchmark function
            memory_benchmark: memory usage of the in-built benchmark function
            digits_for_printing: how many digits should be used by rounder.signif()?
            log_to_file (bool): log results to a file or not?
            log_file (pathlib.Path): path to log file
        """
        self.defaults = {
            "time": {"number": 100_000, "repeat": 5},
            "memory": {"repeat": 1},
        }
        self.settings = {}
        self._benchmark_time()
        self._benchmark_memory()

        # Set up the number of digits to be used in rounder.signif_object(),
        # which rounds numbers to a significant number of digits
        self.digits_for_printing = 4

        self.log_to_file = True
        self.log_file = Path(os.getcwd()) / "perftester.log"

    @property
    def digits_for_printing(self):
        return self._digits_for_printing

    @digits_for_printing.setter
    def digits_for_printing(self, value):
        check_type(
            value,
            int,
            message=f"Argument value must be an int, not {type(value).__name__}",
        )
        self._digits_for_printing = value

    @property
    def log_to_file(self):
        return self._log_to_file

    @log_to_file.setter
    def log_to_file(self, value):
        check_type(
            value,
            bool,
            message=f"Argument value must be an int, not {type(value).__name__}",
        )
        self._log_to_file = value

    @property
    def log_file(self):
        return self._log_file

    @log_file.setter
    def log_file(self, path):
        path = Path(path)
        check_if_paths_exist(
            path.parent.absolute(),
            LogFilePathError,
            f"Argument path must be a valid path",
        )
        self._log_file = path

    @staticmethod
    def cut_traceback():
        """Remove traceback from exceptions, and report only exceptions.

        This is the default behavior of perftester, as when testing performance,
        you do not look for bugs in code, so no need to analyze traceback.
        """
        sys.tracebacklimit = 0

    @staticmethod
    def full_traceback():
        """Use full traceback to report exceptions."""
        sys.tracebacklimit = None

    def reload_time(self):
        """Reload built-in time benchmarks.

        This is done so that a new relative test is run against a built-in
        benchmark that has just been ran, not some time ago.
        """
        self._benchmark_time()

    def reload_memory(self):
        """Reload built-in memory benchmarks.

        This is done so that a new relative test is run against a built-in
        benchmark that has just been ran, not some time ago.

        WARNING: This method is NOT used in normal circumstances because memory
        usage checks do not change over time, so there is no need to update them.
        You need to use this method only when you change the benchmark function.
        """
        self._benchmark_memory()

    def get_setting(self, func, which, item):
        """Get setting (number or repeat) for a function.

        If they were not set up, the default value is provided.

        Args:
            func (Callable): a callable for which the setting is to be changed
            which (str): either "time" or "memory", for which the setting is
                to be changed
            item (str): either "repeat" or "number"
        """
        whiches = ("time", "memory")
        items = ("number", "repeat")
        check_type(
            func,
            Callable,
            IncorrectArgumentError,
            message="Argument func must be a callable.",
        )
        check_argument(
            which,
            expected_type=str,
            expected_choices=whiches,
            handle_with=IncorrectArgumentError,
            message=(
                "Argument which must be str from among "
                f"{_str_iterable(whiches)}"
            ),
        )
        check_argument(
            item,
            expected_type=str,
            expected_choices=items,
            handle_with=IncorrectArgumentError,
            message=(
                "Argument item must be str from among "
                f"{_str_iterable(items)}"
            ),
        )
        check_if_not(
            which == "memory" and item == "number",
            IncorrectArgumentError,
            "For memory tests, you can only set repeat, not number",
        )

        return self.settings.get(func, self.defaults).get(which).get(item)

    def benchmark_function(self):
        """In-built function for benchmarking.

        It's basically an empty function that does nothing, so it's cost
        (time and memory) represent the cost of calling a function. Anything
        more, thus, results from whatever the function is doing.
        """
        pass

    def _benchmark_time(self):
        """Run timeit.repeat for the in-built benchmark function.

        Do note that unlike timeit functions, this one returns a time
        of one function call, so is normalized by "number".

        Returns:
            float: the minimal time from time.repeat per one function call
        """
        self.time_benchmark = (
            min(
                timeit.repeat(
                    lambda: self.benchmark_function,
                    number=self.defaults["time"]["number"],
                    repeat=self.defaults["time"]["repeat"],
                )
            )
            / self.defaults["time"]["number"]
        )

    def _benchmark_memory(self):
        """Run memory_profiler.memory_usage for the in-built benchmark function.

        Returns:
            float: the minimum maximum memory usage over time across all runs.
        """
        memory_results = [
            memory_usage((self.benchmark_function, (), {}))
            for _ in range(self.defaults["memory"]["repeat"])
        ]
        self.memory_benchmark = MiB_TO_MB_FACTOR * min(
            max(r) for r in memory_results
        )

    def set_defaults(
        self, which, number=None, repeat=None, Number=None, Repeat=None
    ):
        """Change the default settings.

        Beware! This does not change particular settings for a particular test,
        but the defaults. So this will affect also how the benchmark tests
        will be run.

        However, this will not change any settings for functions that were already
        set using self.set, or which were already used in perftester.

        Args:
            which (str): either "time" or "memory"
            number (int, optional): passed to timeit.repeat as number.
                Defaults to None.
            repeat (int, optional): passed to timeit.repeat as repeat.
                Defaults to None.
        """
        if number is None and Number is not None:
            number = Number
        if repeat is None and Repeat is not None:
            repeat = Repeat

        self._check_args(lambda: 0, which, number, repeat)

        if number is not None:
            self.defaults[which]["number"] = number
        if repeat is not None:
            self.defaults[which]["repeat"] = repeat

    def set(
        self, func, which, number=None, repeat=None, Number=None, Repeat=None
    ):
        """Set a particular argument.

        Args:
            func (Callable): a callable for which we want to change
                the setting
            which (str): either "time" or "memory"
            number (int, optional): passed to timeit.repeat as number.
                Defaults to None.
            repeat (int, optional): for time tests, passed to timeit.repeat
                as repeat; for memory tests, the number of runs of the test.
                Defaults to None.
        """
        if number is None and Number is not None:
            number = Number
        if repeat is None and Repeat is not None:
            repeat = Repeat

        self._check_args(func, which, number, repeat)

        if func not in self.settings.keys():
            self.settings[func] = {}
            self.settings[func]["memory"] = dict(
                repeat=self.defaults["memory"]["repeat"]
            )
            self.settings[func]["time"] = dict(
                number=self.defaults["time"]["number"],
                repeat=self.defaults["time"]["repeat"],
            )

        if number is not None:
            self.settings[func][which]["number"] = number
        # Below, which must be "memory"; this is checked by ._check_args() above,
        # so we do not have to worry about that here.
        if repeat is not None:
            self.settings[func][which]["repeat"] = repeat

    def _check_args(self, func, which, number, repeat):
        """Check instances of arguments func, which, number and repeat."""
        check_type(
            func,
            Callable,
            IncorrectArgumentError,
            message=(
                "Argument func must be an int (or None), not "
                f"{type(func).__name__}"
            ),
        )

        whiches = ("time", "memory")
        if which is not None:
            check_argument(
                which,
                expected_type=str,
                expected_choices=whiches,
                handle_with=IncorrectArgumentError,
                message=(
                    "Argument which must be str from among "
                    f"{_str_iterable(whiches)}"
                ),
            )
            check_if_not(
                which == "memory" and number is not None,
                IncorrectArgumentError,
                "For memory tests, you can only set repeat, not number.",
            )

        if number is not None:
            if int(number) == number:
                number = int(number)
        if repeat is not None:
            if int(repeat) == repeat:
                repeat = int(repeat)
        check_type(
            number,
            (int, None),
            IncorrectArgumentError,
            message=(
                "Argument number must be an int (or None), not "
                f"{type(number).__name__}"
            ),
        )
        check_type(
            repeat,
            (int, None),
            IncorrectArgumentError,
            message=(
                "Argument repeat must be an int (or None), not "
                f"{type(repeat).__name__}"
            ),
        )


# Create a single instance of Config; this is done when the perftester module is imported.
config = Config()


def _str_iterable(an_iterable):
    """Format an_iterable as a string with items seperated with commas.

    Args:
        an_iterable (iterable): an iterable to be printed as
            a comma-seperated list

    Returns:
        str: a string with a comma-separated list of elements of an_iterable

    >>> _str_iterable({'x', 'z', 'a'})
    'a, x, z'
    >>> _str_iterable(set({'a': 20, 'g': 300, 'eeee': 300}.keys()))
    'a, eeee, g'
    """
    return ", ".join((str(i) for i in sorted(list(an_iterable))))


def _repeat(func, *args, Number=None, Repeat=None, **kwargs):
    """Run timeit.repeat for func.

    This is a simple wrapper for timeit.repeat which uses config.
    Note that the results are normalized by the number of runs,
    so the actual result is the mean execution time of a single
    run of func.

    Args:
        func (Callable): a callable to be tested

    Returns:
        list: the results of timeit.repeat
    """
    number = Number or config.get_setting(func, "time", "number")
    repeat_results = timeit.repeat(
        lambda: func(*args, **kwargs),
        number=number,
        repeat=Repeat or config.get_setting(func, "time", "repeat"),
    )
    return [r / number for r in repeat_results]


def time_test(
    func,
    *args,
    raw_limit=None,
    relative_limit=None,
    Number=None,
    Repeat=None,
    **kwargs,
):
    """Run time performance test for func.

    You need to provide either raw_limit or relative_limit, or both.

    Note that if the tested function throws an error, so will time_test(),
    which will raise the FunctionError exception.

    When you use Number and Repeat, they have a higher priority than
    the corresponding settings from config.settings, and so they will be used.
    They are used in this single call only, and so it does not overwrite
    the config settings.

    Param:
        func (Callable): a function (or any callable) to be tested; passed
            to timeit.repeat
        raw_limit (float): raw limit for the test. It is the maximum time
            that a single run of the function can take; if it's exceeded,
            the test does not pass.
        relative_limit (float): relative limit for the test. It is used for
            relative testing (against a standard function defined in the
            config)
        args, kwargs: arguments passed to func

    Return:
        Nothing when the test passes; TimeTestError is raised otherwise
        (it then provides the limit and the measured time)

    >>> def f(n): return list(range(n))
    >>> first_run = time_benchmark(f, n=10)

    Note that this should have added the function to the config:
    >>> config.settings.keys() #doctest: +ELLIPSIS
    dict_keys([<function ...
    >>> assert_instance(first_run['raw_times'], list)
    >>> assert_instance(first_run['raw_times'][0], float)

    First, let's conduct only raw tests, comparing raw execution times (in sec).
    >>> first_run['min']  < 1e-05
    True
    >>> time_test(f, raw_limit=1e-04, n=1000)
    >>> time_test(f, raw_limit=1e-10, n=1000) #doctest: +ELLIPSIS
    Traceback (most recent call last):
       ...
    perftester.TimeTestError: Time test not passed for function f:
    raw_limit = 1e-10
    minimum run time = ...

    You can see what is the time for the benchmark function from config using
    config.benchmark_time. We cannot do it here, in the doctest, as it depends
    on the machine. However, you can use it to learn what to expect on your
    machine. You use it so in the following way (which here means that the
    tested function should not be slower than the benchmark time from config -
    that's why 1 in limits):
    >>> time_test(f, relative_limit=1, n=10) #doctest: +ELLIPSIS
    Traceback (most recent call last):
       ...
    perftester.TimeTestError: Time test not passed for function f:
    relative_limit = 1
    minimum time ratio = ...

    In our case, the test does not passes (correctly). It will surely pass if we use
    a factor of 10:
    >>> time_test(f, relative_limit=10, n=10)

    This approach based on relative becnhmarks is usuallyt what you want to
    use, since it does not use with direct time (which depends on the machine).
    Instead, we compare our the execution time of the tested function with
    the execution time of the in-built standard function (defined in the
    config), run in the same machine in which the test is run.

    Let's see if the tested function is ten times quicker than the bechmark (it is not):
    >>> time_test(f, relative_limit=.1, n=10)  #doctest: +ELLIPSIS
    Traceback (most recent call last):
       ...
    perftester.TimeTestError: Time test not passed for function f:
    relative_limit = 0.1
    minimum time ratio = ...

    """
    check_if_not(
        raw_limit is None and relative_limit is None,
        LackingLimitsError,
        message="You must provide raw_limit, relative_limit or both",
    )
    _add_func_to_config(func)

    results = time_benchmark(
        func, *args, Number=Number, Repeat=Repeat, **kwargs
    )

    config.cut_traceback()
    # Test raw_limit
    if raw_limit is not None:
        check_if(
            results["min"] <= raw_limit,
            handle_with=TimeTestError,
            message=(
                f"Time test not passed for function {func.__name__}:\n"
                f"raw_limit = {raw_limit}\n"
                f"minimum run time = {rounder.signif(results['min'], config.digits_for_printing)}"
            ),
        )

    # Test the relative time (against the benchmark function)
    if relative_limit is not None:
        ratio_time = results["min"] / config.time_benchmark
        check_if(
            ratio_time <= relative_limit,
            handle_with=TimeTestError,
            message=(
                f"Time test not passed for function {func.__name__}:\n"
                f"relative_limit = {relative_limit}\n"
                f"minimum time ratio = {rounder.signif(ratio_time, config.digits_for_printing)}"
            ),
        )
    config.full_traceback()


def memory_usage_test(
    func,
    *args,
    raw_limit=None,
    relative_limit=None,
    Repeat=None,
    **kwargs,
):
    """Test memory usage of a function.

    You can run a test based on a raw limit for the time of executing
    of the function (this is a time per single run); then use raw_limit to
    provide the limit and relative_limit=None. You can use relative_limit to set up
    a limit for a relative test (against a function defined in the config);
    then use raw_limit=None. But you can also use both at the same time, and
    the tests passes only when both the raw and the relative tests pass.

    When you use Repeat, it has a higher priority than the corresponding
    setting from config.settings, and it will be used. This is used in this
    single call only, and so it does not overwrite the config settings.

    WARNING: Unlike memory_profiler.memory_usage(), which reports memory in MiB,
    perftester provides data in MB.

    Args:
        func (Callable): the tested function.
        raw_limit (float): raw limit for the test. It is the maximum memory
            that the function can use; if it's exceeded, the test does not pass.
        relative_limit (float): relative limit for the test. It is used for
            relative testing (against a standard function defined in the
            config)
        memory_limits (limits): an instance of namedtupe limits, with
            raw_limit and relative_limit attributes. The former is the maximum
            memory that function can use; if it's exceeded, the test does not
            pass. The latter is used for relative benchmarking (against
            a standard function defined in the config); if memory_limits is
            None, the function will provide the memory usage times, which can
            be used to define the limits to be used in testing
        Repeat (int): a repeat setting, overwriting (for this function call)
            the setting in config.settings[func]["memory"]["repeat"]
        *args, **kwargs: arguments passed to the function
     Returns:
        when memory_limit is None, a dict:
            'raw_results': all results (through time), as returned from several
                runs of memory_profile.memory_usage
            'mean_result_per_run': a list of mean results per run
            'max_result_per_run': the maximum result per run (which is perhaps
                the most interesting to us)
            'mean': the mean of the means
            'max': the overall max (so, the maximum usage of memory across all
                runs)
        when memory_limits is not None:
            Nothing when the test passes; perftesterError is raised otherwise
            (it then provides the limit and the measured memory usage)
    >>> def sum1(n): return sum([i**2 for i in range(n)])
    >>> first_run = memory_usage_benchmark(sum1, n=100_000)
    >>> first_run.keys()
    dict_keys(['raw_results', 'relative_results', 'mean_result_per_run', 'max_result_per_run', 'max_result_per_run_relative', 'mean', 'max', 'max_relative'])
    >>> type(first_run['raw_results'])
    <class 'list'>
    >>> first_run['mean'] < first_run['max']
    True
    >>> memory_usage_test(sum1, raw_limit=first_run['max']*2, n=100_000)
    """
    check_type(
        func,
        Callable,
        IncorrectArgumentError,
        "Argument func must be a callable.",
    )
    check_if_not(
        raw_limit is None and relative_limit is None,
        LackingLimitsError,
        message="You must provide raw_limit, relative_limit or both",
    )
    results = memory_usage_benchmark(func, *args, Repeat=Repeat, **kwargs)

    config.cut_traceback()
    if raw_limit is not None:
        check_if(
            results["max"] <= raw_limit,
            handle_with=MemoryTestError,
            message=(
                f"Memory test not passed for function {func.__name__}:\n"
                f"memory_limit = {raw_limit}\n"
                f"maximum memory usage = {rounder.signif(results['max'], config.digits_for_printing)}"
            ),
        )
    if relative_limit is not None:
        relative_got_memory = results["max"] / config.memory_benchmark
        check_if(
            relative_got_memory <= relative_limit,
            handle_with=MemoryTestError,
            message=(
                f"Memory test not passed for function {func.__name__}:\n"
                f"relative memory limit = {relative_limit}\n"
                f"maximum obtained relative memory usage = "
                f"{rounder.signif(relative_got_memory, config.digits_for_printing)}"
            ),
        )
    config.full_traceback()


def memory_usage_benchmark(func, *args, Repeat=None, **kwargs):
    """Run memory benchmarks for a callable.

    It offers an easy way to run benchmarks before defining limits in
    memory_usage_test(). The benchmarks use the settings from config for func,
    or defaults if this function has no settings yet. Note that after
    running the benchmark function for a function, this function will
    be added to config.settings.

    When you use Repeat, it has a higher priority than the corresponding
    setting from config.settings, and it will be used. This is used in this
    single call only, and so it does not overwrite the config settings.

    The function returns a dict that you can pretty-print using function pp().

    WARNING: Unlike memory_profiler.memory_usage(), which reports memory in MiB,
    perftester provides data in MB.

    Args:
        func (Callable): a function (or a callable) to run benchmarks for
        Repeat (int): a repeat setting, overwriting (for this function call)
            the setting in config.settings[func]["memory"]["repeat"]
        *args, **kwargs: arguments passed to func

    Returns:
        dict: a dictionary with results returned by time_test() and
            memory_usage_test()

    >>> def f(x): return x
    >>> f_bench = memory_usage_benchmark(f, x=10)
    >>> f_bench.keys()
    dict_keys(['raw_results', 'relative_results', 'mean_result_per_run', 'max_result_per_run', 'max_result_per_run_relative', 'mean', 'max', 'max_relative'])
    """
    check_type(func, Callable, message="Argument func must be a callable.")
    _add_func_to_config(func)

    n = Repeat or config.settings[func]["memory"]["repeat"]

    try:
        memory_results = [memory_usage((func, args, kwargs)) for i in range(n)]
    except Exception as e:
        raise FunctionError(
            f"The tested function raised {type(e).__name__}: {str(e)}"
        )

    for i, result in enumerate(memory_results):
        for j, _ in enumerate(result):
            memory_results[i][j] *= MiB_TO_MB_FACTOR

    memory_results_mean = [mean(this_result) for this_result in memory_results]
    memory_results_max = [max(this_result) for this_result in memory_results]
    overall_mean = mean(memory_results_mean)
    # We take the min of the max values
    overall_max = min(memory_results_max)

    relative_results = copy.deepcopy(memory_results)
    for i, result in enumerate(relative_results):
        for j, r in enumerate(result):
            relative_results[i][j] = r / config.memory_benchmark

    return {
        "raw_results": memory_results,
        "relative_results": relative_results,
        "mean_result_per_run": memory_results_mean,
        "max_result_per_run": memory_results_max,
        "max_result_per_run_relative": [
            r / config.memory_benchmark for r in memory_results_max
        ],
        "mean": overall_mean,
        "max": overall_max,
        "max_relative": overall_max / config.memory_benchmark,
    }


def time_benchmark(func, *args, Number=None, Repeat=None, **kwargs):
    """Run time benchmarks for a callable.

    It offers an easy way to run benchmarks before defining limits in
    time_test(). The benchmarks use the settings from config for func,
    or defaults if this function has no settings yet. Note that after
    running the benchmark function for a function, this function will
    be added to config.settings.

    The function returns a dict that you can pretty-print using function pp().

    Args:
        func (Callable): a function (or a callable) to run benchmarks for
        Number (int): a number setting, overwriting (for this function call)
            the setting in config.settings[func]["memory"]["number"]
        Repeat (int): a repeat setting, overwriting (for this function call)
            the setting in config.settings[func]["time"]["repeat"]
        *args, **kwargs: arguments passed to func

    Returns:
        dict:
            'raw_times': all the received times (from each repeat)
            'raw_times_relative': all the received times (from each repeat),
                divided by config.benchmark_time
            'min': the minimum time (from the repeats)
            'mean': mean times
            'max': the maximum time
            'max_relative': the maximum time, divided by config.benchmark_time

    >>> def f(x): return x
    >>> f_bench = time_benchmark(f, x=10)
    >>> f_bench.keys()
    dict_keys(['min', 'min_relative', 'raw_times', 'raw_times_relative', 'mean', 'max'])

    Of course, we do have to remember that the execution time can depend on
    the function's arguments:
    >>> def f(n): return list(range(n))
    >>> time_benchmark(f, n=1000)["min"] > time_benchmark(f, n=1)["min"]
    True

    """
    check_type(func, Callable, message="Argument func must be a callable.")
    _add_func_to_config(func)

    try:
        results = _repeat(func, *args, Number=Number, Repeat=Repeat, **kwargs)
    except Exception as e:
        raise FunctionError(
            f"The tested function raised {type(e).__name__}: {str(e)}"
        )

    min_result = min(results)

    # Reload built-in benchmarks
    config.reload_time()

    return {
        "min": min_result,
        "min_relative": min_result / config.time_benchmark,
        "raw_times": results,
        "raw_times_relative": [
            result / config.time_benchmark for result in results
        ],
        "mean": mean(results),
        "max": max(results),
    }


def pp(*args):
    """Pretty print of args.

    If any numbers are among the data, they are rounded to the number of
    significant digits as given by config.digits_for_printing (the default
    is 4). If more than one argument is provided, they are printed with a
    line break used as a separator.

    >>> pp(.122242)
    0.1222
    >>> pp(dict(a=.12121212, b=23.234234234), ["system failure", 345345.345])
    {'a': 0.1212, 'b': 23.23}
    ['system failure', 345300.0]
    >>> t = time_benchmark(lambda: 0, Number=1, Repeat=1)
    >>> pp(t)
    Time data are printed in seconds.
    {'max': ...,
     'mean': ...,
     'min': ...,
     'min_relative': ...,
     'raw_times': [...],
     'raw_times_relative': [...]}
    >>> m = memory_usage_benchmark(lambda: 0)
    >>> pp(m)
    Memory data are printed in MB.
    {'max': ...,
     'max_relative': ...,
     'max_result_per_run': [...],
     'max_result_per_run_relative': [...],
     'mean': ...,
     'mean_result_per_run': [...],
     'raw_results': [[..., ..., ...]],
     'relative_results': [[..., ..., ...]]}
    """
    for arg in args:
        is_benchmark = _check_if_benchmarks(arg)
        if is_benchmark == "time benchmark":
            print("Time data are printed in seconds.")
        elif is_benchmark == "memory benchmark":
            print("Memory data are printed in MB.")
        pprint(
            rounder.signif_object(
                arg, digits=config.digits_for_printing, use_copy=True
            )
        )


def _check_if_benchmarks(obj):
    """Check if obj comes from time or memory benchmarks.

    >>> _check_if_benchmarks(10)
    >>> _check_if_benchmarks("10")
    >>> _check_if_benchmarks([10, ])
    >>> _check_if_benchmarks((10, ))
    >>> _check_if_benchmarks({10, 20})
    >>> _check_if_benchmarks(dict(x=10, y=20))
    >>> t = time_benchmark(lambda: 0, Number=1, Repeat=1)
    >>> m = memory_usage_benchmark(lambda: 0)
    >>> _check_if_benchmarks(t)
    'time benchmark'
    >>> _check_if_benchmarks(m)
    'memory benchmark'
    """
    time_keys = {
        "min",
        "min_relative",
        "raw_times",
        "raw_times_relative",
        "mean",
        "max",
    }
    memory_keys = {
        "raw_results",
        "relative_results",
        "mean_result_per_run",
        "max_result_per_run",
        "max_result_per_run_relative",
        "mean",
        "max",
        "max_relative",
    }
    try:
        if obj.keys() == time_keys:
            return "time benchmark"
    except AttributeError:
        pass
    try:
        if obj.keys() == memory_keys:
            return "memory benchmark"
    except AttributeError:
        return None


def _add_func_to_config(func):
    if func not in config.settings.keys():
        config.settings[func] = {}
        config.settings[func]["time"] = dict(
            number=config.defaults["time"]["number"],
            repeat=config.defaults["time"]["repeat"],
        )
        config.settings[func]["memory"] = dict(
            repeat=config.defaults["memory"]["repeat"],
        )


if __name__ == "__main__":
    import doctest

    flags = flags = (
        doctest.ELLIPSIS
        | doctest.NORMALIZE_WHITESPACE
        | doctest.IGNORE_EXCEPTION_DETAIL
    )
    doctest.testmod(optionflags=flags)
