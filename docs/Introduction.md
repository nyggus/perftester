# `perftest`: Simple performance testing for Python

`perftest` is a lightweight package for simple performance testing in Python. Here, performance refers to execution time and memory usage, so performance testing means testing if a function performs quickly enough and does not use too much RAM. In addition, the module offers you simple functions for straightforward benchmarking, in terms of both execution time and memory.

The idea behind the package is to enable the user to write simple performance tests. They can be used in `doctest`s and `pytest`s, but first of all, `perftest` offers its own performance testing framework, which you should rather prefer, since performance tests can be time-consuming. Thus, it's better not to mix unit and performance tests.

The module assumes simplicity, which means simplicity at two levels:
* simple performance tests, so that you do not need make far-going assumptions about the tests - you can first run benchmarks, see what's going on, and use them to create tests; and
* simple coding, so that you can write these tests quickly and without too much hassle.

This assumption, however, also means that the module offers simple performance testing (which you can include in your code easily and quickly). Thus, if you need something more complex, you should look for other tools. This means that `perftest` does not aim to replace complex performance testing, but rather to 
* help you conduct simple performance testing during development, in order to watch out whether a recent change in code did not affect the performance of the application; and
* help you include simple automated performance tests in a production environment, so that the tests can catch changes in the application's performance.

> Always remember that time-based performance testing strongly depends on all the processes that a machine is running, so you can get quite varying results from run to run. Hence, it's wise to set safe limits for your tests.


### `perftest` as a benchmarking tool

Although `perftest` mainly offers a testing tool, it can also be treated as a benchmarking tool that enables you to easily benchmark time and memory use of a function. You can use two functions: `time_benchmark()` and `memory_usage_benchmark()`. You can treat them as simple benchmarking tools for a function, you can use them to compare the performance of two (or more) functions, but you can also use the function for setting up limits to be used for a particular function.

See [here](#simple-benchmarking) for examples.


## Raw and relative performance testing using `perftest`

Surely, any performance tests are strongly environment-dependent, so you need to remember that when writing and conducting any performance tests. `perftest`, however, offers a solution to this: You can define tests based on

* raw values: raw execution time and raw memory usage, and
* relative values: relative execution time and relative memory usage

Above, _relative_ means benchmarking against a built-in (into `perftest`) simple function. Thus, you can, for instance, test whether your function is two times slower than this function. The benchmarking function itself does not matter, as it is just a benchmark. What matters is that, usually, your function should _relatively to this benchmarking function_ behave the same way between different machines. So, if it works two times slower than the benchmarking function on your machine, then it should work in a similar way on another machine, even if this other machine is much faster than yours. Of course, this assumes linearity (so, two times slower here means two times slower everywhere), which does not have to be always true. Anyway, such tests will almost always be more representative, and more precise, than those based on raw times.

This does not mean, however, that raw tests are useless. In fact, in a production environment, you may wish to use raw tests. Imagine a client expects that an app never takes longer than an hour to perform a particular task (note that this strongly depends on what other processes are run in the production environment). You can create an automated test for that using `perftest`, in a very simple way - just several lines of code.

You can of course combine both types of tests, and you can do it in a very simple way. Then, the test is run once, but the results are checked with raw limits and relative limits.


## Installation

Install using `pip`:

```shell
pip install perftest
```

The package has three external dependencies: [`memory_profiler`](https://pypi.org/project/memory-profiler/) ([repo](https://github.com/pythonprofilers/memory_profiler)), [`easycheck`](https://pypi.org/project/easycheck/) ([repo](https://github.com/nyggus/easycheck)), and [`rounder`](https://pypi.org/project/rounder/) ([repo](https://github.com/nyggus/rounder)).


## Use

The `perftest` package comes with four functions: `time_test()`, `time_benchmark()`, `memory_usage_test()`, and `memory_usage_benchmark()`. The first one enables you to conduct performance testing in time context, while the third in memory-use context; the other two enable you to perform the corresponding benchmarks.


## Configuration

The package comes with configuration for tests. It's an instance of a (singleton) class `Config`, which you can check after the first import:

```
>>> import perftest as pt
>>> type(pt.config)
<class 'perftest.perftest.Config'>

```

Now it's practically empty, but after running some benchmarks and/or tests, it will keep settings for all these functions. You can read more about how to use `perftest.config` [here](use_of_config.md).


### `time_test()`

`time_test()` uses `timeit.repeat()`. It enables you to test a function, not a code snippet (in fact, `time.repeat()` also enables you to do that).


#### Raw time testing

This is how you can check the performance (in terms of time) of your function. In order to make the tests run quick enough, let's decrease the default `number` to 10K.

```python
>>> def f(n): return list(range(n))
>>> pt.config.set(f, "time", number=10_000)

```

Note that when calling `pd.config.set()`, we provided

* the function (`f`) for which we want to change settings;
* the argument `which`, which can be either `"time"` or `"memory"`;
* and the argument you want to change (`number`); in the same way, you can change `repeat`.

Let's run the benchmark:


```python
>>> first_run = pt.time_benchmark(f, n=1000)

```

Here, `n=1000` means that we want to run `f(1000)`; you can provide here any `*args` and `**kwargs` that the function requires. The function returns a dictionary with the following keys:

```python
>>> first_run.keys()
dict_keys(['min', 'min_relative', 'raw_times', 'raw_times_relative', 'mean', 'max'])

```

Dictionary `first_run`, in my machine, shows the following results:

```python
# pt.pp(first_run)
{'raw_times': [2.718e-05, 2.633e-05, 2.831e-05, 2.789e-05, 2.961e-05],
 'raw_times_relative': [339.7, 329.0, 353.7, 348.5, 370.1],
 'max': 2.961e-05,
 'mean': 2.786e-05,
 'min': 2.633e-05,
 'min_relative': 329.0}
 ```

Note that list `"raw_times"` contains mean values per single run of the function. Remember this, because this is a different approach than that taken by `timeit` functions (`timeit.timeit()` and `timeit.repeat()`), which provide results summarized for all runs. Here, the results need to be normalized, in order to make it easy to define a test and then change its settings (that is, `number`) without the necessity to change the limits. So, the effect of `number` is different here than in `timeit` functions, in which the bigger the `number`, the bigger the execution times. In `perftest`, `number` affects the precision of the result (the more runs of the function, the less standard error of the estimation of the mean time). This approach has also one particular advantage: You can see how much time the function needs to run on your machine.

We're ready to define test limits. Of course, they should be a little higher than those obtained in the above benchmarks. Do remember that these results depend also on all the other processes your machine is running.

```python
>>> pt.time_test(f, raw_limit=6e-05, n=1000)

```

Running the above test should return nothing and throw nothing. Like with `pytest`s and `doctest`s, this means that the test has passed. If a test fails (below it will, because we will make the raw time limit an unrealistic zero), the following happens:

```python
>>> pt.time_test(f, raw_limit=0, n=1000) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.TimeTestError: Time test not passed for function f:
raw_limit = 0
minimum run time = ...

```

(In my machine, the `minimum run time` was about 8.3e-06, but since this README serves as doctests, we had to use the ellipsis functionality of `doctest`.)


#### Relative time testing

A relative time-related test can look like this:

```python
>>> pt.time_test(f, relative_limit=700, n=1000)

```

The value of 700 means that the tested function should be at most 700 times slower than the benchmarking function (that is, a function doing nothing). Don't pay too much attention to the interpretion of this factor, as it depends on the `pt.config.benchmark_function()`, which does not really lie within our interest, although it does inform us about something: it's an empty function (`def foo(): pass`), so it represents an overhead cost of calling a function. You can overwrite this function and use your own one, if you wish (see [here](change_benchmarking_function.md)). The point is that thanks to such a relative approach, you can be more or less sure that the test will behave the same way in your machine, in a much slower machine, and also in a much quicker one. This would unlikely be the case when using raw approach to time-performance testing.

However, you can compare the relative results between functions. Consider another function:

```python
>>> import array
>>> def f2(n): return array.array("i", range(n))

```

And now let's run the same test, but with a smaller `n` (to save time in `doctest`s):

```python
>>> pt.time_test(f, relative_limit=9, n=10)
>>> pt.time_test(f2, relative_limit=9, n=10) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.TimeTestError: Time test not passed for function f2:
relative_limit = 9
minimum time ratio = ...

```

In my machine, the `minumum time ratio` for `f2()` was about 12.65, so bigger than that for `f()`. 


### `memory_usage_test()`

`memory_usage_test()` uses `memory_profiler.memory_usage()` to run tests. Its default behavior is to run the test only once, as it does not make sense to repeat `memory_profiler.memory_usage()`: it will take almost the same time throughout the runs. There can be some exceptions, however; for instance, when a function has some random component and does not know at compile time how much memory it will have to allocate. For such situations, `perftest` enables you to set `repeat` for a particular function in memory tests. You can do so using `pt.config.set()`, for instance in the following way: `pt.config.set(my_function, "memory", repeat=10)`. (Note there is no `number` argument used for memory testing.)


### Raw memory usage testing

This is how you can check the performance in terms of memory use of your function:

```python
>>> first_run = pt.memory_usage_benchmark(f, n=1000)

```

This is what `first_run` returned on my machine:

```python
{'max': 16.77,
 'max_relative': 1.004,
 'max_result_per_run': [16.77],
 'max_result_per_run_relative': [1.004],
 'mean': 16.77,
 'mean_result_per_run': [16.77],
 'raw_results': [[16.77, 16.77, 16.77]],
 'relative_results': [[1.003, 1.004, 1.004]]}
```

> Function `f` uses very little memory. You can check that by benchmarking a function `def foo(): pass`, which will basically use the same memory as `f()` did.

Note the three values in `raw_results`. `memory_profiler.memory_usage()` measures memory use over time, and these are the results. The number of such measurements depends on the function. Read more 

We can see that this function does not change memory usage over time. This is because we're creating small lists, of 1000 elements. Let's see the results for a list of 10 million elements:

```python
# pt.pp(pt.memory_usage_test(f, None, n=10000000))
{'max': 403.1,
 'max_relative': 24.02,
 'max_result_per_run': [403.1],
 'max_result_per_run_relative': [24.02],
 'mean': 202.5,
 'mean_result_per_run': [202.5],
 'raw_results': [[16.78, 17.14, 138.1, 258.5, 381.3, 403.1]],
 'relative_results': [[1.0, 1.021, 8.229, 15.4, 22.72, 24.02]]}
```

Quite a difference. The actual tests use `"max"` for raw testing and `"max_relative"` for relative testing, but the function provides all of these values, so you can understand the performance of your function. Clearly, for a big list, `f`'s memory use does increase with time. Let's see the same for `f2`, which uses `array.array`. On my machine, `pt.pp(pt.memory_usage_test(f2, None, n=10_000_000))` provided the following results:

```python
# pt.pp(pt.memory_usage_test(f2, None, n=10_000_000))
{'max': 55.65,
 'max_relative': 3.265,
 'max_result_per_run': [55.65],
 'max_result_per_run_relative': [3.265],
 'mean': 36.2,
 'mean_result_per_run': [36.2],
 'raw_results': [[17.04, 17.06, 25.15, 32.71, 40.05, 47.67, 54.3, 55.65]],
 'relative_results': [[1.0, 1.001, 1.476, 1.919, 2.35, 2.797, 3.186, 3.265]]}
```

That's quite a difference! Clearly, `array.array` is optimized in terms of memory use. Let's see how the two functions compare in terms of execution time when `n` is that big. But for this, we have to change `number` to a far smaller one - let's make it 10 (`pt.config.set(f, "time", number=10); pt.config.set(f2, "time", number=10)`). Here are the results for `f()` (create a list of 10 mln elements):

```python
# pt.pp(pt.time_test(f, None, n=10_000_000))
{'raw_times': [0.4041, 0.4024, 0.4352, 0.4305, 0.4417],
 'raw_times_relative': [4613000.0, 4594000.0, 4968000.0, 4915000.0, 5042000.0],
 'max': 0.4417,
 'mean': 0.4228,
 'min': 0.4024,
 'min_relative': 4594000.0}
```

 and compare them with those for `f2()` (create an `array.array` of 10 mln integers):

```python
# pt.pp(pt.time_test(f2, None, n=10_000_000))
{'raw_times': [0.5654, 0.5522, 0.5494, 0.5463, 0.5422],
 'raw_times_relative': [6854000.0, 6693000.0, 6659000.0, 6622000.0, 6572000.0],
 'max': 0.5654,
 'mean': 0.5511,
 'min': 0.5422,
 'min_relative': 6572000.0}
```

So, although `array.array` uses far less memory, it does take a little more time to create a 10-mln array of integers than does a function creating a list of integers. However, the gain in memory use of `array.array` over the list is much bigger than the list's gain in execution time over `array.array`.


### Relative memory usage testing

Like with `time_test`, you can also use relative testing:

```python
>>> pt.memory_usage_test(f2, relative_limit=5, n=10_000_000)
>>> pt.memory_usage_test(f, relative_limit=2, n=10_000_000) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.MemoryTestError: Memory test not passed for function f:
relative memory limit = 2
maximum obtained relative memory usage = ...

```


## Relative tests against another function

In the basic use, when you choose a relative benchmark, you compare the performance of your function with that of a built-in (empty) function `pt.config.benchmark_function()`. In most cases, this is what you need. Sometimes, however, you may wish to benchmark against another function. For instance, you may want to build your own function that does the same thing as a Python built-in function, and you want to test (and show) that your function performs better. There are two ways of achieving this:

* you can use a simple trick; [see here](benchmarking_against_another_function.md);
* you can overwrite the built-in benchmark functions; [see here](change_benchmarking_function.md).


## Simple benchmarking

The `perftest` module offers `time_benchmark()` and `memory_usage_benchmark()` functions that enable you to run both types of benchmarks (type- and memory-related) with one command. Both functions use settings from `perftest`'s `config` in the very same way as the two corresponding testing functions (`time_test()` and `memory_usage_test()`).

Let's see some examples. I will change the default settings, so that the doctests do not take too much time and the results are not too long:

```python
>>> pt.config.set_defaults("time", repeat=1, number=10)

```

Note that although it does not change the settings for the functions that `pt.config` already contains, but all new functions will use the new defaults.

```python
>>> def sum_of_squares(x): return sum(i**2 for i in x)
>>> def square_of_sum(x): return sum(x)**2
>>> x = [1.0002, 56.0303, 780, 0.1, 445.55553, 190.01, 56.76]*100_000
>>> time_bench_sum_of_squares = pt.time_benchmark(sum_of_squares, x)
>>> memory_bench_sum_of_squares = pt.memory_usage_benchmark(sum_of_squares, x)
>>> time_bench_square_of_sum = pt.time_benchmark(square_of_sum, x)
>>> memory_bench_square_of_sum = pt.memory_usage_benchmark(square_of_sum, x)

```

We can see the benchmarks using the `pt.pp()` function. In my machine, this gives the following results:

```python
# pt.pp(memory_bench_sum_of_squares)
{'max': 21.96,
'max_relative': 1.0,
'max_result_per_run': [21.96],
'max_result_per_run_relative': [1.0],
'mean': 21.96,
'mean_result_per_run': [21.96],
'raw_results': [[21.96,
                    21.96,
                    21.96,
                    21.96,
                    21.96,
                    21.96,
                    21.96,
                    21.96]],
'relative_results': [[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]}

# pt.pp(time_bench_sum_of_squares)
{'raw_times': [0.05726],
'raw_times_relative': [238600.0],
'max': 0.05726,
'mean': 0.05726,
'min': 0.05726,
'min_relative': 238600.0}

# pt.pp(memory_bench_square_of_sum)
{'max': 21.98,
'max_relative': 1.0,
'max_result_per_run': [21.98],
'max_result_per_run_relative': [1.0],
'mean': 21.98,
'mean_result_per_run': [21.98],
'raw_results': [[21.98, 21.98, 21.98, 21.98]],
'relative_results': [[1.0, 1.0, 1.0, 1.0]]

# # pt.pp(time_bench_square_of_sum)
{'raw_times': [0.002721],
'raw_times_relative': [10880.0],
'max': 0.002721,
'mean': 0.002721,
'min': 0.002721,
'min_relative': 10880.0}
```

We can see that both functions use more or less the same memory, but, expectedly, `square_of_sum()` uses much less time than `sum_of_square()`.

You can use these results to compare the performance of the functions, but also to define `raw_limits` and `relative_limits` for `time_test()` and `memory_usage_test()`.


## Other tools

Of course, Python comes with various powerful tools for profiling, benchmarking and testing. Here are some of them:

* [`cProfile` and `profile`](https://docs.python.org/3/library/profile.html), the built-in powerful tools for deterministic profiling
* [the built-in `timeit` module](https://docs.python.org/3/library/timeit.html), for benchmarking
* [`memory_profiler`](https://pypi.org/project/memory-profiler/), a powerful memory profiler (`memory_profiler` is utilized by `perftest`)
  
In fact, `perftest` is just a simple wrapper around `timeit` and `memory_profiler`, since `perftest` itself does not come with its own solutions. It simply uses these functions and offers an easy-to-use API to benchmark and test memory and time performance.


## Additional notes

#### Manipulating the traceback

The default behavior of `perftest` is to **not** include the full traceback when a test does not pass. This is because when running performance tests, you're not interested in finding bugs, and this is what traceback is for. Instead, you want to see which test did not pass and how.

> Remember that if you use `perftest` in an interactive session, you may want to change this behavior. You can do it by calling a dedicated method in `pt.config`: `pt.config.full_trace()`.
