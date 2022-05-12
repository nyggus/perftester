# `perftest`: Lightweight performance testing of Python functions

`perftest` is a lightweight package for simple performance testing in Python. Here, performance refers to execution time and memory usage, so performance testing means testing if a function performs quickly enough and does not use too much RAM. In addition, the module offers you a simple function for straightforward benchmarking, in terms of both execution time and memory.

Under the hood, `perftest` is a wrapper around two functions from other modules:
* `perftest.time_test()` uses `timeit.repeat()`
* `perftest.memory_usage_test()` uses `memory_profiler.memory_usage`

What `perftest` offers is a testing framework with as simple syntax as possible.

You can use `perftest` in three main ways:
* in an interactive session, for simple benchmarking of functions;
* as part of another testing framework, like `doctest` or `pytest`s; and
* as an independent testing framework.

The first one is a different type of use from the other two. I use it to learn the behavior of functions I am working on right now, so not for actual testing. Instead, I heavily use `pt.benchmark()` function, which helps me analyze both memory use and execution time of functions. (Actually, to save some typing, in an interactive session I like to use `b = pt.benchmark`, or even `def b(func, *args, **kwargs): pt.pp(pt.benchmark(func, *args, **kwargs))` and then I use `b` function. But this is something one can do solely in an interactive session, and definitely when no one is picking from your back at what you're doing.)

It's difficult to say which of the last two is better: it may depend on how many performance tests you have, and how much time they take. If the tests do not take more than a couple of seconds, then you should consider combining them with unit tests. But if they take much time, you should likely make them independent of unit tests, and run them from time to time. (It's good to have unit tests that run quickly.)

> This document is a short introduction to `perftest`. You can learn a lot more in [this heavy introduction](docs/Introduction.md) and in the other files in the [docs](docs/) folder.


## Using `perftest`

### Use it as a separate testing framework

To use `perftest` that way,

* Collect tests in Python modules whose names start with "perftest_", for instance, "perftest_module1.py", perftest_module2.py" and the like.
* Inside these modules, collect testing functions that start with "perftest_", for instance, "def perftest_func_1()", "def perftest_func_2()", and the like (note how similar these two points are to how `pytest` is run);
* You can create a config_perftest.py file, in which you can change any configuration you want, using the `perftest.config` object. The file should be located in the folder from which you will run the CLI command `perftest`. If this file is not there, `perftest` will simply use its default configuration.
* Now you can run the `perftest` in your shell. You can do it in three ways:
  * `$ perftest` recursively collects all `perftest` modules from the directory in which the command was run, and from all its subdirectories; then it runs all the tests/
  * `$ perftest path_to_dir` recursively collects all `perftest` modules from path_to_dir/ and runs all their tests.
  * `$ perftest path_to_file.py` runs all tests from the `perftest` module given in the path;

Read more about using perftest that way here.

> It **does** make a difference how you do that. When you run the `perftest` command with each testing file independently, each file will be tested in a new session, so with a new instance of the `pt.config` object. When you run the command for a directory, all the functions will be tested in one session. And when you run a bare `perftest` command, all your tests will be run in one session/

> There is no best approach, but remember to choose one that suits your needs.


### Use `perftest` inside `pytest`

This is a very simple approach, perhaps the simplest one: When you use `pytest` you can simply add `perftest` testing functions to `pytest` testing functions, and that way both frameworks will be combined, or rather the `pytest` framework will use `perftest`. The amount of additional work is minimal. 

For instance, you can write the following test function:

```python
import perftest as pt
from my_module import f1 # assume that f1 takes two arguments, a string (x) and a float (y)
def test_performance_of_f1():
    pt.time_test(f1, pt.limits(10, None), x="whatever string", y=10.002)

```

and that's all you need! (We will discuss `perftest` functions in a minute.) If you now run `pytest` and the test passes, nothing will happen - just like with a regular `pytest` test. If the test fails, however, a `perftest.TimeError` exception will be thrown, with some additional information.

This is the easiest way to use `perftest`. Its only drawback is that if the performance tests take much time, `pytest` will take too much time, something definitely to be avoided. You can then do some `pytest` tricks to not run `perftest` tests, and run them only when you want - or you can simply use the above-described command-line `perftest` framework for performance testing.


### Use `perftest` inside `doctest`

In the same way, you can use `perftest` in `doctest`. You will find plenty of examples in the documentation here, and in the [tests/ folder](tests/). For instance, in the docstring of `f1()` (used above), you could write:
```python
>>> def f1(x: str, y: float):
...     """Function that does something with x and y.
...     Performance test:
...     >>> import perftest as pt
...     >>> pt.time_test(f1, pt.limits(10, None), x="whatever string", y=10.002)
...     """
...     pass

```

> A great fan of `doctest`ing, I do **not** recommend such an approach - for me, `doctest`s in docstrings should clarify things and explain how the functions works. I would not say that adding a performance test to a function's docstring will increase readability. You can, however, write performance tests as separate `doctest` files, and then collect them in a shell script that runs these files, that way running performance tests.


## Basic use of `perftest`

As mentioned above, you can learn far more in [this heavy introduction](docs/Introduction.md) and in the other files in the [docs](docs/) folder. Here, we will only show the basic use of `perftest`, to picture how it can be used and how simply it is to use.

### Simple benchmarking

To create a test, you likely need to know how a function behaves. You can run a simple benchmarking function, `pt.benchmark`, which will run both time and memory benchmarks. First, we need to decrease `number` (passed to `timeit.repeat`), in order to shorten the benchmarks (which here serve as doctrests):

```
>>> import perftest as pt
>>> def f(n): return sum(map(lambda i: i**0.5, range(n)))
>>> pt.config.set(f, "time", number=1000)
>>> b_100 = pt.benchmark(f, n=100)
>>> b_1000 = pt.benchmark(f, n=1000)

```
And this is it. You can use `pt.pp()` function to pretty-print the results. In my machine, I got the following results (here, for b_100):

```python
# pt.pp(b_100)
{'memory': {'max': 16.66,
            'max_relative': 1.004,
            'max_result_per_run': [16.66],
            'max_result_per_run_relative': [1.004],
            'mean': 16.66,
            'mean_result_per_run': [16.66],
            'raw_results': [[16.66, 16.66, 16.66]],
            'relative_results': [[1.004, 1.004, 1.004]]},
 'time': {'max': 1.389e-05,
          'mean': 1.303e-05,
          'min': 1.168e-05,
          'min_relative': 129.5,
          'raw_times': [1.168e-05, 1.263e-05, 1.349e-05, 1.346e-05, 1.389e-05],
          'raw_times_relative': [129.5, 140.0, 149.5, 149.2, 154.0]}}
```

For `memory`, the main result is `max` while for test, it is `min`. For relative testing (see [this introduction](docs/Introduction.md) for details) , we would look at `max_relative` and `min_relative`, respectively.

Surely, we should expect that the function with `n=100` be quicker than with `n=1000`:

```python
>>> b_100["time"]["min"] < b_1000["time"]["min"]
True

```

but memory use will be more or less the same:

```python
>>> .99 < (b_100["memory"]["max"] / b_1000["memory"]["max"]) < 1.01
True

```

### Time testing

For time tests, we have `pt.time_test()` function. First, a raw time test:


```python
>>> pt.time_test(f, pt.limits(2e-05, None), n=100)

```

Now, a relative time test:

```python
>>> pt.time_test(f, pt.limits(None, 150), n=100)

```

But we can combine both:

```python
>>> pt.time_test(f, pt.limits(2e-05, 150), n=100)

```

> You can see the use of `pt.limits`, a `collections.namedtuple` with two fields: `raw_limit` and `relative_limit`. See [here](docs/use_of_limits.md).

Relative tests test against the time that a built-in function (into the `config`) took to execute. This function does not matter, but the point is to compare relative execution time, as it should be more or less the same across different machines, even those on which raw times could differ quite a lot.


### Time testing

Memory tests use `pt.memory_usage_test()` function, which is used in the same way as `pt.time_test()`:

```python
>>> pt.memory_usage_test(f, pt.limits(20, None), n=100) # test on raw memory
>>> pt.memory_usage_test(f, pt.limits(None, 1.01), n=100) # relative time test
>>> pt.memory_usage_test(f, pt.limits(20, 1.01), n=100) # both

```

Of course, memory tests do not make that much sense for function that do not have to allocate too much memory, but as you will see in other documentation files in `perftest`, some function do use a lot of memory, and such tests for them do make quite a lot sense.


## `pt.config`

The whole configuration is stored in the `pt.config` object, which you can easily change. See more [here](docs/use_of_config.md). When you use `perftest` as a command-line tool, you can modify `pt.config` in the `settings_perftest.py` module, for instance:

```python
# settings_perftest.py
import perftest as pt

# shorten the tests
pt.config.set_defaults("time", number=10_000, repeat=3) 

# log the results to file (they will be printed in the console anyway)
pt.config.log_to_file = True
pt.config.log_file = "./perftest.log"

# increase the digits for printing floating numbers
pt.config.digits_for_printing = 7

```

and so on. You can also change settings in each testing file itself, preferably in `perftest_` functions.

When you use `perftest` in an interactive session, you simply update `pt.config` in a normal way.

When you use it with perftest, you can do it in conftest.py and in each testing function.


## Output

If a test fails, you will see something like this:

```shell
# for time test
TimeError in perftest_for_testing.perftest_f
Time test not passed for function f:
raw_limit = 0.011
minimum run time = 0.1007

# for memory test
MemoryError in perftest_for_testing.perftest_f2_time_and_memory
Memory test not passed for function f2:
memory_limit = 20
maximum memory usage = 20.04
```

So, this is what you can see in this output:

* Whether it's an error from a time test (`TimeError`) or a memory test (`MemoryError`).
* `perftest_for_testing.perftest_f` provides the testing module (`perftest_for_testing`) and the perftest function (`perftest_f`).
* `Memory test not passed for function f2:`: Here you see for which tested (not `perftest_`) function the test failed.
* `raw_limit` and `memory_limit`: these are the raw limits you provided; these could be also `relative_limit` and `relative memory limit`, for relative tests.
* `minimum run time` and `maximum memory usage` are the actual results from testing, and they were too high (higher than the limits set inside the testing function).

You can locate where a particular test failed, using the module, `perftest_` function, and tested function. If a `perftest_` function combines more tests, then you can find the failed test using the limits.

> Like in `pytest`, a recommended approach is to use one performance test per `perftest_` function. This can save you some time and trouble, but also this will ensure that all tests will be run.


#### Summary output

At the end, you will see a simple summary of the results, something like this:

```shell
Out of 8 tests, 5 has passed and 3 has failed.

Passed tests:
perftest_for_testing.perftest_f2
perftest_for_testing.perftest_f2_2
perftest_for_testing.perftest_f2_3
perftest_for_testing.perftest_f3
perftest_for_testing_2.perftest_f

Failed tests:
perftest_for_testing.perftest_f
perftest_for_testing.perftest_f2_time_and_memory
perftest_for_testing.perftest_f_2
```

## Caveats

* `perftest` does not work with multiple threads or processes.
* `perftest` is still in a beta version and so is still under heavy testing.


## Operating systems

The package is developed in Linux (actually, under WSL) and checked in Windows 10.


## Support

Any contribution will be welcome. You can submit an issue in the [repository](https://github.com/nyggus/perftest). You can also create your own pull requests.
