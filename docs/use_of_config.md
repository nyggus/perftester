# Use of `perftester.config`

When you import `perftester`, `config`, an instance of `Config`, is created:

```python
>>> import perftester as pt
>>> pt.config #doctest: +ELLIPSIS
<perftester.perftester.Config object at ...

```

> As `Config` is a singleton class, in one session, only one instance of `Config` is created, and it is indeed called `config`.

This object contains all you need to change settings of your `perftester`s. Let's see what it includes at the beginning, in addition to in-built methods:

```python
>>> [i for i in dir(pt.config) if not i.startswith("_")]
['benchmark_function', 'config_file', 'cut_traceback', 'defaults', 'digits_for_printing', 'full_traceback', 'get_setting', 'log_file', 'log_to_file', 'memory_benchmark', 'reload_memory', 'reload_time', 'set', 'set_defaults', 'settings', 'time_benchmark']

```

Let's go through these attributes and methods one by one.

### `.benchmark_function()`

This is a method that is used for benchmarking. This is a very simple function:

```python
def benchmark_function(self):
    return [i ** 2 for i in (1, 100, 1000)]

```

Whenever you perform a relative performance check, your tested function's performance is divided by `benchmark_function`'s performance. You can read more about this [here](/docs/change_benchmarking_function.md).


### `.benchmark_memory()` and `.benchmark_time()`

These two methods run benchmarks of `.benchmark_function` for memory use and execution time. You do not hate to use them, since they are run when `pt.config` is being instantiated, in `.__init__`.


### `.reload()`

This method reloads the benchmarks of the built-in function. This is in fact not needed for the memory benchmarks, since the results will not change to any meaningful level. However, time benchmarks can change, so before running any benchmark, `time_test()` runs `pt.config.reload("time")`, so you do not need to worry about that.

Most likely, there is only one situation in which you would need to call this method, and that's overwriting the built-in benchmarking function. It's described [here](/docs/change_benchmarking_function.md).


### `.defaults`

The `defaults` attribute is the following dictionary:

```python
>>> import perftester as pt
>>> pt.config.defaults
{'time': {'number': 100000, 'repeat': 5}, 'memory': {'repeat': 1}}

```
It contains default settings: for `"time"` (that is, time tests), `number=1_000_000` and `repeat=5`; and for `"memory"`, `repeat=1`. If you run tests for a particular function and its setting have not been changed, these defaults will be used. They are also used by `.benchmark_time` and `.benchmark_memory`.

You can change them, using method `.set_defaults()` (see below), but do this with caution - if you want to change a setting for a particular function, you can do so using method `.set`. It's best to change defaults if you want to use them in all your tests.


### `.get_setting()`

This simply gives you `number` or `repeat` (provided as a string to argument `item`) for a particular function (provided as argument `func`);  you also need to specify `which`, which can be either `"test"` or `"memory"`. If there are no settings for such a function, defaults are returned. Look:

```python
>>> def f1(): pass
>>> pt.config.get_setting(func=f1, which="time", item="repeat")
5

```

### `.memory_benchmark` and `.time_benchmark`

These attributes keeps the maximum used RAM and the minimum execution time measured during benchmarks of `.benchmark_function()`.

### `.set()`

Use this method to change a setting for a particular function:

```python
>>> pt.config.set(f1, "time", repeat=1)
>>> pt.config.set(f1, "memory", repeat=2)
>>> pt.config.get_setting(func=f1, which="time", item="repeat")
1

>>> pt.config.get_setting(func=f1, which="memory", item="repeat")
2

```

For `which="time"`, you can change both settings at the same time:

```python
>>> pt.config.set(f1, "time", Repeat=3, Number=1000)
>>> pt.config.get_setting(f1, "time", "repeat")
3
>>> pt.config.get_setting(f1, "time", "number")
1000

```

### '.set_defaults()'

This method can be used in the very same way as above-described `.set()`, but this one changes the default settings:

```python
>>> pt.config.set_defaults("time", Repeat=3, Number=5000)
>>> pt.config.defaults
{'time': {'number': 5000, 'repeat': 3}, 'memory': {'repeat': 1}}

>>> def new_func(): pass
>>> pt.config.get_setting(new_func, "time", "number")
5000

```

but do remember that this does not affect any settings for functions with already changed settings **and** for those for which you already run tests:

```python
>>> pt.config.get_setting(f1, "time", "number")
1000

```


### `.settings`

This attribute simply contains the settings for any function for which they were stored, including those functions that were tested using either `time_test()` or `memory_test()`:

```python
>>> pt.config.settings #doctest: +ELLIPSIS
{<function f1 at ...>: {'memory': {'repeat': 2}, 'time': {'number': 1000, 'repeat': 3}}}

>>> def f2(): return 0
>>> _ = pt.time_benchmark(f2)

>>> pt.config.settings #doctest: +ELLIPSIS
{<function f1 at ...>: {'memory': {'repeat': 2}, 'time': {'number': 1000, 'repeat': 3}}, <function f2 at ...>: {'time': {'number': 5000, 'repeat': 3}, 'memory': {'repeat': 1}}}

```

Notice in the last example that it is enough to run a test for a new function, and this function will appear in `pt.config.settings`.

You do not need to directly use this attribute. `perftester` functions use them, and you can change them using the `.set()` method.


### Traceback

As `perftester` does not aim to catch bugs in your code, you need not see and analyze the full traceback after a test does not pass. Hence, the default behavior is to print only the error itself, without the traceback.

You can change this behavior using `.full_traceback()` method, and then change back using `.cut_traceback()`.


### `.digits_for_printing`

The `.digits_for_printing` controls the way `pp` rounds numbers, but also the way exceptions are printed. The default is 4, and this number is passed to `rounder.signif()` and `rounder.signif_object()` functions. Note:

```python
>>> pt.pp({"a": 1.123123, "b": 3434.3434})
{'a': 1.123, 'b': 3434.0}

>>> pt.config.digits_for_printing = 3
>>> pt.pp({"a": 1.123123, "b": 3434.3434})
{'a': 1.12, 'b': 3430.0}

>>> pt.config.digits_for_printing = 5
>>> pt.pp({"a": 1.123123, "b": 3434.3434})
{'a': 1.1231, 'b': 3434.3}

```

Using the default values, you could for instance get the following exception:

```python
perftester.perftester.MemoryTestError: Memory test not passed for function f:
relative memory limit = 2.0
maximum obtained relative memory usage = 3.321
```

but with `pt.config.digits_for_printing = 7`, you would get this:

```python
perftester.perftester.MemoryTestError: Memory test not passed for function f:
relative memory limit = 2.0
maximum obtained relative memory usage = 3.321411
```

Feel free to change `pt.config.digits_for_printing` if the default value of 4 does not meet your needs.
