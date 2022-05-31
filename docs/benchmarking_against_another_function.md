# Benchmark a function against another function

In basic use, when you choose a relative benchmark, you compare the performance of your function with that of a built-in function `pt.config.benchmark_function()`, the definition of which is very simple:

```python
def benchmark_function(self):
    return [i ** 2 for i in (1, 100, 1000)]

```

More often than not you do't need anything else. But sometimes you may want to benchmark your function against a different function, usually one that means something in the context of your project. For instance, you may want to build your own function that does the same thing as a Python built-in function (or a function from another external Python package), and you want to test that your function performs better.


# Benchmarking the two functions

Most of the times, first, you need to conduct benchmarks for both functions, to see how they perform, unless you have some assumptions that you want or have to use in the tests. 

So, we have the following two functions (which we used in README) and we want to test `f2()` against `f()`:

```python
>>> def f(n): return list(range(n))
>>> import array
>>> def f2(n): return array.array("i", range(n))

```

Let's check the performance of both functions for large `n`, for which the way memory is allocated can make a difference. (For the purpose of `doctest`s used in this file, we will change benchmark settings; this will also make the results short enough to be presented here.)

```python
>>> import perftest as pt
>>> pt.config.set_defaults("time", number=10, repeat=1) # change defaults - both functions will use these settings
>>> n_for_comparison = 10_000_000

# Actual benchmarks
>>> f_performance_time = pt.time_benchmark(f, n=n_for_comparison)
>>> f_performance_memory = pt.memory_usage_benchmark(f, n=n_for_comparison)
>>> f2_performance_time = pt.time_benchmark(f2, n=n_for_comparison)
>>> f2_performance_memory = pt.memory_usage_benchmark(f2, n=n_for_comparison)

```

This is what I got on my machine:

```python
# pt.pp(f_performance_memory)
{'max': 403.0,
'max_relative': 24.34,
'max_result_per_run': [403.0],
'max_result_per_run_relative': [24.34],
'mean': 202.7,
'mean_result_per_run': [202.7],
'raw_results': [[16.69, 17.02, 137.6, 260.9, 380.9, 403.0]],
'relative_results': [[1.008, 1.028, 8.308, 15.76, 23.0, 24.34]]}

# pt.pp(f_performance_time)
{'raw_times': [0.4279],
'raw_times_relative': [1711000.0],
'max': 0.4279,
'mean': 0.4279,
'min': 0.4279,
'min_relative': 1711000.0}

# pt.pp(f2_performance_memory)
{'max': 55.12,
'max_relative': 3.329,
'max_result_per_run': [55.12],
'max_result_per_run_relative': [3.329],
'mean': 35.34,
'mean_result_per_run': [35.34],
'raw_results': [[16.97,
                 16.97,
                 23.96,
                 31.38,
                 39.19,
                 45.75,
                 53.36,
                 55.12]],
'relative_results': [[1.025,
                      1.025,
                      1.447,
                      1.895,
                      2.367,
                      2.763,
                      3.223,
                      3.329]]}

# pt.pp(f2_performance_time)
{'raw_times': [0.5504],
'raw_times_relative': [1966000.0],
'max': 0.5504,
'mean': 0.5504,
'min': 0.5504,
'min_relative': 1966000.0}

```

What we can see is that `f2()`, which uses `array.array`, takes a little more time than does `f()`:

```python
>>> f_performance_time["min"] < f2_performance_time["min"]
True

```

At the same time, `f2()` employs much less memory. When looking at the maximum memory use (`memory_usage_test()` takes this approach), it's over 5 times less memory:

```python
>>> f_performance_memory["max"] / f2_performance_memory["max"] > 5
True

```


# Creating a time performance test of `f2()` against `f()`

OK, we have our benchmarks, so we can set up limits for both time and memory testing. Say, we want to test `f2()` against `f()`. Let's say, we want to test whether it does not take more time than 300% of `f()`, for `n` of 10_000_000. You can do it in the following way:

```python
>>> pt.time_test(
...    f2,
...    raw_limit=3 * f_performance_time["min"],
...    relative_limit=None,
...    n=n_for_comparison
... )

```

Often, however, you will not run such benchmarks before running tests, so in actual tests, you would do it in the following way:

```python
>>> pt.time_test(
...    f2,
...    raw_limit=3 * pt.time_benchmark(f, n=n_for_comparison)["min"],
...    relative_limit=None,
...    n=n_for_comparison
... )

```

If you do it that way, first the test for `f()` is run and then that for `f2()`. So, here you are, this is a time-performance test of `f2()` relative to `f()`. Now let's do it for memory.


# Creating a memory performance test of `f2()` against `f()`

Basically, we're doing the same thing, but for memory. When we analyzed the benchmarks, we noted that `f2()` uses over 5 times less memory than does `f()`. Let's build a relative test that `f2()` uses the maximum of 6 times less memory than `f()` uses. This is a version with `f_performance`:

```python
>>> pt.memory_usage_test(
...    f2,
...    f_performance_memory["max"] / 6,
...    None,
...    n=n_for_comparison
... )

```

and here is a direct version, running both tests with one command:

```python
>>> pt.memory_usage_test(
...    f2,
...    pt.memory_usage_benchmark(f, n=n_for_comparison)["max"] / 6,
...    None,
...    n=n_for_comparison
... )

```


> Note that while for `time_test()` we used `["min"]`, for `memory_usage_test` we have to use `["max"]`, as we are benchmarking against the maximum RAM used throughout the time of executing the function.