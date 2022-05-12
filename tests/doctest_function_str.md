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
>>> pt.time_test(preprocess, None, 123)
Traceback (most recent call last):
    ...
perftest.perftest.FunctionError: The tested function raised TypeError: expected string or bytes-like object

>>> pt.memory_usage_test(preprocess, None, 123)
Traceback (most recent call last):
    ...
perftest.perftest.FunctionError: The tested function raised TypeError: expected string or bytes-like object

>>> pt.benchmark(preprocess, 123)
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
>>> results_time = pt.time_test(preprocess, None, "123")
>>> assert_instance(results_time, dict)
>>> results_time.keys()
dict_keys(['min', 'min_relative', 'raw_times', 'raw_times_relative', 'mean', 'max'])

>>> exp_l = pt.config.get_setting(preprocess, "time", "repeat") # expected length, as defined in config
>>> assert_length(results_time["raw_times"], exp_l)
>>> assert_length(results_time["raw_times_relative"], exp_l)
>>> assert_if(results_time["mean"] >= results_time["min"])
>>> assert_if(results_time["max"] >= results_time["mean"])

```

##  Testing `memory_usage_test()` function

```python
>>> results_memory = pt.memory_usage_test(preprocess, None, "123")
>>> assert_instance(results_memory, dict)
>>> results_memory.keys()
dict_keys(['raw_results', 'relative_results', 'mean_result_per_run', 'max_result_per_run', 'max_result_per_run_relative', 'mean', 'max', 'max_relative'])

>>> assert_length(results_memory["max_result_per_run_relative"], 1)
>>> assert_length(results_memory["max_result_per_run"], 1)
>>> assert_length(results_memory["relative_results"], 1)
>>> assert_length(results_memory["raw_results"], 1)
>>> assert_if(results_memory["max"] >= results_memory["mean"])

```

##  Testing `benchmark()` function

```python
>>> results_bench = pt.benchmark(preprocess, "123")
>>> assert_instance(results_bench, dict)
>>> results_bench.keys()
dict_keys(['time', 'memory'])
>>> assert_instance(results_bench["time"], dict)
>>> assert_instance(results_bench["memory"], dict)

```

#### Tests of the `"time"` part

```python
>>> assert_length(results_bench["time"]["raw_times"], exp_l)
>>> assert_length(results_bench["time"]["raw_times_relative"], exp_l)
>>> assert_if(results_bench["time"]["max"] >= results_bench["time"]["mean"])

```

#### Tests of the `"memory"` part:

```python
>>> results_memory.keys()
dict_keys(['raw_results', 'relative_results', 'mean_result_per_run', 'max_result_per_run', 'max_result_per_run_relative', 'mean', 'max', 'max_relative'])

>>> assert_length(results_bench["memory"]["max_result_per_run_relative"], 1)
>>> assert_length(results_bench["memory"]["max_result_per_run"], 1)
>>> assert_length(results_bench["memory"]["relative_results"], 1)
>>> assert_length(results_bench["memory"]["raw_results"], 1)
>>> assert_if(results_bench["memory"]["max"] >= results_bench["memory"]["mean"])

```