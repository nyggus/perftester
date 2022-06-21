# Tests: Case study for strings


## Imports and the tested function

```python
>>> import perftest as pt
>>> from easycheck import assert_instance, assert_length, assert_if
>>> import re

```

A function to be tested (just a function with some string manipulations, nothing fancy):

```python
>>> def preprocess(text):
...    return re.sub(r'[^\w\s]', '', text)

```


## Errors

Note that when an exception is raised from the tested function, the `perftest` functions will throw the `perftest.FunctionError` error, which will contain the original error, too:

```python
>>> pt.time_test(preprocess, 123, raw_limit=1)
Traceback (most recent call last):
    ...
perftest.perftest.FunctionError: The tested function raised TypeError: expected string or bytes-like object

>>> pt.memory_usage_test(preprocess, 123, raw_limit=1)
Traceback (most recent call last):
    ...
perftest.perftest.FunctionError: The tested function raised TypeError: expected string or bytes-like object

>>> pt.time_benchmark(preprocess, 123)
Traceback (most recent call last):
    ...
perftest.perftest.FunctionError: The tested function raised TypeError: expected string or bytes-like object

>>> pt.memory_usage_benchmark(preprocess, 123)
Traceback (most recent call last):
    ...
perftest.perftest.FunctionError: The tested function raised TypeError: expected string or bytes-like object

```


## `pt.config`

After running the first test, the `preprocess` function should occur in `pt.config`'s settings:

```python
>>> preprocess in pt.config.settings.keys()
True

```

## Testing `time_test()` function

```python
>>> results_time = pt.time_test(preprocess, "123", raw_limit=1)

>>> results_time = pt.time_test(preprocess, "123", relative_limit=10)

```

##  Testing `memory_usage_test()` function

```python
>>> results_memory = pt.memory_usage_test(preprocess, "123", raw_limit=20)

>>> results_memory = pt.memory_usage_test(preprocess, "123", relative_limit=3)

```

##  Testing `time_benchmark()` function

```python
>>> results_bench_time = pt.time_benchmark(preprocess, "123")
>>> assert_instance(results_bench_time, dict)
>>> exp_l = pt.config.get_setting(preprocess, "time", "repeat") # expected length, as defined in config
>>> assert_length(results_bench_time["raw_times"], exp_l)
>>> assert_length(results_bench_time["raw_times_relative"], exp_l)
>>> assert_if(results_bench_time["max"] >= results_bench_time["mean"])
>>> results_bench_time.keys()
dict_keys(['min', 'min_relative', 'raw_times', 'raw_times_relative', 'mean', 'max'])

```

## Testing `memory_usage_benchmark()` function

```python
>>> results_bench_memory = pt.memory_usage_benchmark(preprocess, "123")
>>> assert_instance(results_bench_memory, dict)

>>> assert_length(results_bench_memory["max_result_per_run_relative"], 1)
>>> assert_length(results_bench_memory["max_result_per_run"], 1)
>>> assert_length(results_bench_memory["relative_results"], 1)
>>> assert_length(results_bench_memory["raw_results"], 1)
>>> assert_if(results_bench_memory["max"] >= results_bench_memory["mean"])

```
