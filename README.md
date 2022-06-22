# `perftest`: Lightweight performance testing of Python functions

## Installation

Install using `pip`:

```shell
pip install perftest
```

The package has three external dependencies: [`memory_profiler`](https://pypi.org/project/memory-profiler/) ([repo](https://github.com/pythonprofilers/memory_profiler)), [`easycheck`](https://pypi.org/project/easycheck/) ([repo](https://github.com/nyggus/easycheck)), and [`rounder`](https://pypi.org/project/rounder/) ([repo](https://github.com/nyggus/rounder)).


## Pre-introduction: TL;DR

At the most basic level, using `perftest` is simple. It offers you two functions for benchmarking (one for execution time and one for memory), and two functions for performance testing (likewise). Read below for a very short introduction of them. If you want to learn more, however, do not stop there, but read on.


### Benchmarking

You have `time_benchmark()` and `memory_benchmark()` functions:

```python
import perftest as pt
def foo(x, n): return [x] * n
pt.time_benchmark(foo, x=129, n=100)
```
and this will print the results of the time benchmark, with raw results similar to those that `timeit.repeat()` returns, but unlike it, `pt.time_benchmark()` returns mean raw time per function run, not overall; in additional, you will see some summaries of the results.

The above call did actually run  `timeit.repeat()` function, with the default configuration of `number=100_000` and `repeat=5`. If you want to change any of these, you can use arguments `Number` and `Repeat`, correspondigly:

```python
pt.time_benchmark(foo, x=129, n=100, Number=1000)
pt.time_benchmark(foo, x=129, n=100, Repeat=2)
pt.time_benchmark(foo, x=129, n=100, Number=1000, Repeat=2)
```

These calls do not change the default settings so you use the arguments' values on the fly. Later you will learn how to change the default settings and the settings for a particular function.

> Some of you may wonder why the `Number` and `Repeat` arguments violate what we can call the Pythonic style, by using a capital first letter for function arguments. The reason is simple: I wanted to minimize a risk of conflicts that would happen when benchmarking (or testing) a function with any of the arguments `number` or `repeat` (or both). A chance that a Python function will have a `Number` or a `Repeat` argument is rather small. If that happens, however, you can use `functools.partial()` to overcome the problem:

```python
def bar(Number, Repeat): return [Number] * Repeat
from functools import partial
bar_p = partial(bar, Number=129, Repeat=100)
pt.time_benchmark(bar_p, Number=100, Repeat=2)
```

Benchmarking RAM usage is similar:

```python
pt.memory_usage_benchmark(foo, x=129, n=100)
```

It uses the `memory_profiler.memory_usage()` function, which runs the function just once to measure its memory use. Almost always, there is no need to repeat it, unless there is great randomness in memory usage by the function. If you have good reasons to change this behavior (e.g., in the case of such randomness), you can request several calls of the function, using the `Repeat` argument:

```python
pt.memory_usage_benchmark(foo, x=129, n=100, Repeat=100)
```

You can learn more in the detailed description of the package below.

### Testing

The API of `perftest` testinf functions is similar to that of benchmarking functions, the only difference being limits you need to provide. You can determine those limits using the above benchmark functions. Here are examples of several performance tests using `perftest`:

```python
# A raw test
>>> pt.time_test(foo, raw_limit=9.e-07, x=129, n=100)

# A relative test
>>> pt.time_test(foo, relative_limit=7, x=129, n=100)

# A raw test
>>> pt.memory_usage_test(foo, raw_limit=25, x=129, n=100)

# A relative test
>>> pt.memory_usage_test(foo, relative_limit=1.01, x=129, n=100)

```

You can, certainly, use `Repeat` and `Number`:

```python
>>> pt.time_test(foo, relative_limit=7, x=129, n=100, Repeat=3, Number=1000)

```

Raw tests work with raw executation time. Relative tests work with relative time against a call of an empty function; that way, the test should be more or less independent of the machine you run the test on; so, a quick machine should provide more or less similar relative results as a slow machine.

> Relative results, however, can differ between different operating systems.

You can use these testing functions in `pytest`, or in dedicated `doctest` files. You can, however, use `perftest` as a separate performance testing framework. Read on to learn more about that. What's more, `perftest` offers more functionalities, and a `config` object that offers you much more control of testing.

That's all in this short introduction. If you're interested in more advanced use of `perftest`, read on to read a far more detailed introduction. In addition, files in the [docs](docs/) folder explain in detail particular functionalities that `perftest` offers.

## Introduction


`perftest` is a lightweight package for simple performance testing in Python. Here, performance refers to execution time and memory usage, so performance testing means testing if a function performs quickly enough and does not use too much RAM. In addition, the module offers you simple functions for straightforward benchmarking, in terms of both execution time and memory.

Under the hood, `perftest` is a wrapper around two functions from other modules:
* `perftest.time_benchmark()` and `perftest.time_test()` use `timeit.repeat()`
* `perftest.memory_usage_benchmark()` and `perftest.memory_usage_test()` use `memory_profiler.memory_usage()`

What `perftest` offers is a testing framework with as simple syntax as possible.

You can use `perftest` in three main ways:
* in an interactive session, for simple benchmarking of functions;
* as part of another testing framework, like `doctest` or `pytest`s; and
* as an independent testing framework.

The first way is a different type of use from the other two. I use it to learn the behavior of functions (interms of execution time and memory use) I am working on right now, so not for actual testing.

When it comes to actual testing, it's difficult to say which of the last two ways is better or more convinient: it may depend on how many performance tests you have, and how much time they take. If the tests do not take more than a couple of seconds, then you can combine them with unit tests. But if they take much time, you should likely make them independent of unit tests, and run them from time to time.


## Using `perftest`

### Use it as a separate testing framework

To use `perftest` that way,

* Collect tests in Python modules whose names start with "perftest_"; for instance, "perftest_module1.py", perftest_module2.py" and the like.
* Inside these modules, collect testing functions that start with "perftest_"; for instance, `def perftest_func_1()`, `def perftest_func_2()`, and the like (note how similar this approach is to that which `pytest` uses);
* You can create a config_perftest.py file, in which you can change any configuration you want, using the `perftest.config` object. The file should be located in the folder from which you will run the CLI command `perftest`. If this file is not there, `perftest` will use its default configuration. Note that cofig_perftest.py is a Python module,so `perftest` configuration is done in actual Python code.
* Now you can run performance tests using `perftest` in your shell. You can do it in three ways:
  * `$ perftest` recursively collects all `perftest` modules from the directory in which the command was run, and from all its subdirectories; then it runs all the collected `perftest` tests;
  * `$ perftest path_to_dir` recursively collects all `perftest` modules from path_to_dir/ and runs all perftests located in them.
  * `$ perftest path_to_file.py` runs all perftests from the module given in the path.

Read more about using perftest that way [here](docs/use_perftest_as_CLI.md).

> It **does** make a difference how you do that. When you run the `perftest` command with each testing file independently, each file will be tested in a separated session, so with a new instance of the `pt.config` object. When you run the command for a directory, all the functions will be tested in one session. And when you run a bare `perftest` command, all your tests will be run in one session.

> There is no best approach, but remember to choose one that suits your needs.


### Use `perftest` inside `pytest`

This is a very simple approach, perhaps the simplest one: When you use `pytest`, you can simply add `perftest` testing functions to `pytest` testing functions, and that way both frameworks will be combined, or rather the `pytest` framework will run `perftest` tests. The amount of additional work is minimal. 

For instance, you can write the following test function:

```python
import perftest as pt
from my_module import f1 # assume that f1 takes two arguments, a string (x) and a float (y)
def test_performance_of_f1():
    pt.time_test(
      f1,
      raw_limit=10, relative_limit=None,
      x="whatever string", y=10.002)
```

This will use either the settings for this particular function (if you set them in `pt.config`) or the default settings (also from `pt.config`). However, you can also use `Number` and `Repeat` arguments, in order to overwrite these settings (passed to `timeit.repeat()` as `number` and `repeat`, respectively) for this particular function call:

```python
import perftest as pt
from my_module import f1 # assume that f1 takes two arguments, a string (x) and a float (y)
def test_performance_of_f1():
    pt.time_test(
      f1,
      raw_limit=10, relative_limit=None,
      x="whatever string", y=10.002
      Number=1_000_000, Repeat=20)
```

If you now run `pytest` and the test passes, nothing will happen — just like with a regular `pytest` test. If the test fails, however, a `perftest.TimeTestError` exception will be thrown, with some additional information.

> `perftest`'s default behavior is to significantly shorten traceback. Therefore, if you use it with `pytest`, you can be a little amazed and disappointed. But it's easy to change this behavior, with just one command: `pt.config.full_traceback()`.

This is the easiest way to use `perftest`. Its only drawback is that if the performance tests take much time, `pytest` will also take much time, something usually to be avoided. You can then do some `pytest` tricks to not run `perftest` tests, and run them only when you want — or you can simply use the above-described command-line `perftest` framework for performance testing.


### Use `perftest` inside `doctest`

In the same way, you can use `perftest` in `doctest`. You will find plenty of examples in the documentation here, and in the [tests/ folder](tests/). 

> A great fan of `doctest`ing, I do **not** recommend using `perftest` in docstrings. For me, `doctest`s in docstrings should clarify things and explain how functions work, and adding a performance test to a function's docstring would decrease readability. 

The best way, thus, is to write performance tests as separate `doctest` files, dedicated to performance testing. You can collect such files in a shell script that runs performance tests.


## Basic use of `perftest`


### Simple benchmarking

To create a performance test for a function, you likely need to know how it behaves. You can run two simple benchmarking functions, `pt.memory_usage_benchmark()` and `pt.time_benchmark()`, which will run time and memory benchmarks, respectively. First, we will decrease `number` (passed to `timeit.repeat`), in order to shorten the benchmarks (which here serve as `doctest`s):

```python
>>> import perftest as pt
>>> def f(n): return sum(map(lambda i: i**0.5, range(n)))
>>> pt.config.set(f, "time", number=1000)
>>> b_100_time = pt.time_benchmark(f, n=100)
>>> b_100_memory = pt.memory_usage_benchmark(f, n=100)
>>> b_1000_time = pt.time_benchmark(f, n=1000)
>>> b_1000_memory = pt.memory_usage_benchmark(f, n=1000)

```

Remember also about the possibility of overwriting (for this single benchmark) the settings from `pt.config.settings`, which you can do using `Number` (only for time testing) and `Repeat` (for both): `pt.time_benchmark(f, n=100, Number=1_000_000, Repeat=20)` and `pt.memory_usage_benchmark(f, n=1000, Repeat=10)`.

And this is it. You can use `pt.pp()` function to pretty-print the results. In my machine, I got the following results (here, for `b_100`):

```python
# pt.pp(b_100_time)
{'max': 16.66,
'max_relative': 1.004,
'max_result_per_run': [16.66],
'max_result_per_run_relative': [1.004],
'mean': 16.66,
'mean_result_per_run': [16.66],
'raw_results': [[16.66, 16.66, 16.66]],
'relative_results': [[1.004, 1.004, 1.004]]}

# pt.pp(b_100_memory)
{'max': 1.389e-05,
'mean': 1.303e-05,
'min': 1.168e-05,
'min_relative': 129.5,
'raw_times': [1.168e-05, 1.263e-05, 1.349e-05, 1.346e-05, 1.389e-05],
'raw_times_relative': [129.5, 140.0, 149.5, 149.2, 154.0]}

```

For memory testing, the main result is `max` while for time testing, it is `min`. For relative testing, we would look at `max_relative` and `min_relative`, respectively.

Surely, we should expect that the function with `n=100` be quicker than with `n=1000`:

```python
>>> b_100_time["min"] < b_1000_time["min"]
True

```

but memory use will be more or less the same:

```python
>>> import math
>>> math.isclose(b_100_memory["max"], b_1000_memory["max"], rel_tol=.01)
True

```

### Time testing

For time tests, we have the `pt.time_test()` function. First, a raw time test:


```python
>>> pt.time_test(f, raw_limit=2e-05, n=100)

```

> `raw_limit`, `relative_limit`, `Number` and `Repeat` are keyword-only arguments.

Like before, we can use `Number` and `Repeat` arguments:

```python
>>> pt.time_test(func=f, raw_limit=3e-05, n=100, Number=10)

```

Now, let's define a relative time test:

```python
>>> pt.time_test(f, relative_limit=230, n=100)

```

We also can combine both:

```python
>>> pt.time_test(f, raw_limit=2e-05, relative_limit=230, n=100)

```

You can read about relative testing below, [in section](#raw-and-relative-performance-testing). 


### Memory testing

Memory tests use `pt.memory_usage_test()` function, which is used in the same way as `pt.time_test()`:

```python
>>> pt.memory_usage_test(f, raw_limit=27, n=100) # test on raw memory
>>> pt.memory_usage_test(f, relative_limit=1.01, n=100) # relative time test
>>> pt.memory_usage_test(f, raw_limit=27, relative_limit=1.01, n=100) # both

```

In a memory usage test, a function is called only once. You can change that — but do that only if you have solid reasons — using, for example, `pt.config.set(f, "time", "repeat", 2)`, which will set this setting for the function in the configuration (so it will be used for all next calls for function `f()`). You can also do it just once (so, without saving the setting in `pt.config.settings`), using the `Repeat` argument:

```python
>>> pt.memory_usage_test(f, raw_limit=27, relative_limit=1.01, n=100, Repeat=100)

```

(There is little sence in repeating this particular function, as you will get almost the same results in each repetition.)

Of course, memory tests do not have to be very useful for functions that do not have to allocate too much memory, but as you will see in other documentation files in `perftest`, some function do use a lot of memory, and such tests do make quite a lot sense for them.


## Configuration: `pt.config`

The whole configuration is stored in the `pt.config` object, which you can easily change. Here's a short example of how you can use it:

```python
>>> def f(n): return list(range(n))
>>> pt.config.set(f, "time", number=10_000, repeat=1)

```

but you can change much more using it. **You can read in detail about using `pt.config` [here](docs/use_of_config.md)**.

When you use `perftest` as a command-line tool, you can modify `pt.config` in the `settings_perftest.py` module, for instance:

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

# Use regular traceback
pt.config.full_traceback()

```

and so on. You can also change settings in each testing file itself, preferably in `perftest_` functions.

When you use `perftest` in an interactive session, you update `pt.config` in a normal way, in the session. And when you use `perftest` inside `pytest`, you can do it in conftest.py and in each testing function.


## Output

If a test fails, you will see something like this:

```shell
# for time test
TimeTestError in perftest_for_testing.perftest_f
Time test not passed for function f:
raw_limit = 0.011
minimum run time = 0.1007

# for memory test
MemoryTestError in perftest_for_testing.perftest_f2_time_and_memory
Memory test not passed for function f2:
memory_limit = 20
maximum memory usage = 20.04
```

Let's analyze what we see in this output:

* Whether it's an error from a time test (`TimeTestError`) or a memory test (`MemoryTestError`).
* `perftest_for_testing.perftest_f` provides the testing module (`perftest_for_testing`) and the perftest function (`perftest_f2_time_and_memory`).
* `Memory test not passed for function f2:`: Here you see for which tested (not `perftest_`) function the test failed (here, `f2()`).
* `raw_limit` and `memory_limit`: these are the raw limits you provided; these could be also `relative_limit` and `relative_memory_limit`, for relative tests.
* `minimum run time` and `maximum memory usage` are the actual results from testing, and they were too high (higher than the limits set inside the testing function).

You can locate where a particular test failed, using the module, `perftest_` function, and the tested function. If a `perftest_` function combines more tests, then you can find the failed test using the limits.

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


## Relative tests against another function

In the basic use, when you choose a relative benchmark, you compare the performance of your function with that of a built-in (empty) function `pt.config.benchmark_function()`. In most cases, this is what you need. Sometimes, however, you may wish to benchmark against another function. For instance, you may want to build your own function that does the same thing as a Python built-in function, and you want to test (and show) that your function performs better. There are two ways of achieving this:

* you can use a simple trick; [see here](benchmarking_against_another_function.md);
* you can overwrite the built-in benchmark functions; [see here](change_benchmarking_function.md).


## Raw and relative performance testing

Surely, any performance tests are strongly environment-dependent, so you need to remember that when writing and conducting any performance tests. `perftest`, however, offers a solution to this: You can define tests based on

* raw values: raw execution time and raw memory usage, and
* relative values: relative execution time and relative memory usage

Above, _relative_ means benchmarking against a built-in (into `perftest`) simple function, which is actually an empty function (so it represents the overhead of running a function). Thus, you can, for instance, test whether your function is two times slower than this function. The benchmarking function itself does not matter, as it is just a benchmark. What matters is that, usually, your function should _relatively to this benchmarking function_ behave the same way between different machines. So, if it works two times slower than the benchmarking function on your machine, then it should work in a similar way on another machine, even if this other machine is much faster than yours. Of course, this assumes linearity (so, two times slower here means two times slower everywhere), which does not have to be always true. Anyway, such tests will almost always be more representative, and more precise, than those based on raw times.

This does not mean, however, that raw tests are useless. In fact, in a production environment, you may wish to use raw tests. Imagine a client expects that an app never takes longer than an hour to perform a particular task (note that this strongly depends on what other processes are run in the production environment). You can create an automated test for that using `perftest`, in a very simple way - just several lines of code.

You can of course combine both types of tests, and you can do it in a very simple way. Then, the test is run once, but the results are checked with raw limits and relative limits.

> Warning! Relative results can be different between operating systems.


## Other tools

Of course, Python comes with various powerful tools for profiling, benchmarking and testing. Here are some of them:

* [`cProfile` and `profile`](https://docs.python.org/3/library/profile.html), the built-in powerful tools for deterministic profiling
* [the built-in `timeit` module](https://docs.python.org/3/library/timeit.html), for benchmarking
* [`memory_profiler`](https://pypi.org/project/memory-profiler/), a powerful memory profiler (`memory_profiler` is utilized by `perftest`)
  
In fact, `perftest` is just a simple wrapper around `timeit` and `memory_profiler`, since `perftest` itself does not come with its own solutions. It simply uses these functions and offers an easy-to-use API to benchmark and test memory and time performance.


## Manipulating the traceback

The default behavior of `perftest` is to **not** include the full traceback when a test does not pass. This is because when running performance tests, you're not interested in finding bugs, and this is what traceback is for. Instead, you want to see which test did not pass and how.

> Remember that if you use `perftest` in an interactive session or inside `pytest`, you may want to change this behavior. You can do it by calling a dedicated method in `pt.config`: `pt.config.full_trace()`.


## Caveats

* `perftest` does not work with multiple threads or processes.
* `perftest` is still in a beta version and so is still under testing.
* Watch out when you're running the same test in different operating systems. Even relative tests can differ from OS to OS.


## Operating systems

The package is developed in Linux (actually, under WSL) and checked in Windows 10, so it works in both these environments.


## Support

Any contribution will be welcome. You can submit an issue in the [repository](https://github.com/nyggus/perftest). You can also create your own pull requests.
