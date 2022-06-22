# Tests: A case study with floating numbers

```python
>>> import perftester as pt

```

## Tested functions

We will calculate a variance of a float variable, provided as a list. We will do so using several versions of the function, with different levels of code optimization.

First, let's define a helper function:

```python
>>> def to_float(x):
...    if x is None:
...        return None
...    try:
...        f_x = float(x)
...    except ValueError:
...        return None
...    return f_x

```

Now, the actual functions to calculate variance:

```python
>>> def variance(a_list):
...    new = [to_float(i) for i in a_list if to_float(i)]
...    var = sum((i - sum(new) / len(new))**2 for i in new) / (len(new) - 1)
...    return var

```

This function can be definitely improved:

```python
>>> def variance_2(a_list):
...    new = [to_float(i) for i in a_list if to_float(i)]
...    n = len(new)
...    mean = sum(new) / n
...    var = sum((i - mean)**2 for i in new) / (n - 1)
...    return var

```

It's possible that the list comprehension can be optimized even more, as it runs `to_float()` twice every iteration:

```python
>>> def variance_3(a_list):
...    new = [to_float(i) for i in a_list]
...    new = [i for i in new if i is not None]
...    n = len(new)
...    mean = sum(new) / n
...    var = sum((i - mean)**2 for i in new) / (n - 1)
...    return var

```

And let's create a generator version. Not only generators can be slower than the corresponding lists, but also, as you will see, this function requires us to define three copies of the generator. So, it's quite possible that this version will not be slower than the above one(s).

```python
>>> import itertools
>>> def variance_4(a_list):
...    new, new_2, new_3 = itertools.tee(
...        (to_float(i) for i in a_list if i is not None),
...        3
...    )
...    n = sum(1 for i in new_2 if i is not None)
...    mean = sum(i for i in new if i is not None) / n
...    var = sum((i - mean)**2 for i in new_3 if i is not None) / (n - 1)
...    return var

```

**Hypothesis**: `variance()` and `variance_4()` (the generator version) are slow. As for `variance()`, it is really poorly written, as `sum(new)` is run as many times as we have elements in the list, and `len(new)` even two times more. Thus, this function will be really slow.  `variance_4()` uses generators, but it uses *three of them*, and generators are rather slower than lists, even if they use less memory. So, this function will also be slow. `variance_2()` does not have the same problems as `variance()`, but its problem is running `to_float()` twice per iteration; hence the solution in `variance_3()` should be quicker, even though it runs two list comprehensions. Thus, `variance_3()` should be the quickest functions among these four, though this does not have to be the same - we're comparing running a list comprehension with two calls of `to_float()` per each iteration *versus* two list comprehensions and only one run of `to_float()` per run (and in only one list comprehension). Let's see.

In some tests, we will the following function:

```python
>>> def is_sorted(a_list, /, *, key=None, reverse=False):
...    return a_list == sorted(a_list, key=key, reverse=reverse)

```

## Time benchmarking

```python
>>> x_short = [4.1, "10", "a", 5.6, 6.4, None, 6.6, 6.7, "6.6", 11.1, 5.6, "33,3", 7.1, "5.2", 10.2, 5.3, 7.4, 6.6, 6.5, 5.5, 10.1, 5.2, 7.2, None, None, None, "opal", ] * 100

>>> variance(x_short), variance_2(x_short), variance_3(x_short), variance_4(x_short) #doctest: +ELLIPSIS
(3.5..., 3.5..., 3.5..., 3.5...)

>>> pt.config.set_defaults("time", number=100)
>>> var_perf_time = pt.time_benchmark(variance, x_short)
>>> var_perf_2_time = pt.time_benchmark(variance_2, x_short)
>>> var_perf_3_time = pt.time_benchmark(variance_3, x_short)
>>> var_perf_4_time = pt.time_benchmark(variance_4, x_short)
>>> var_perf_memory = pt.memory_usage_benchmark(variance, x_short)
>>> var_perf_2_memory = pt.memory_usage_benchmark(variance_2, x_short)
>>> var_perf_3_memory = pt.memory_usage_benchmark(variance_3, x_short)
>>> var_perf_4_memory = pt.memory_usage_benchmark(variance_4, x_short)

>>> var_perf_time["min"] > var_perf_4_time["min"]
True
>>> var_perf_time["min"] > var_perf_2_time["min"]
True
>>> var_perf_time["min"] > var_perf_3_time["min"]
True
>>> var_perf_2_time["min"] > var_perf_3_time["min"]
True
>>> var_perf_4_time["min"] > var_perf_3_time["min"]
True

```

Differences between the four functions are significant, particularly `variance()` is much slower than the others, and `variance_4()` is much slower than both `variance_2()` and `variance_3()`. You can see the results I got on  my machine [here](results_of_floats.md).


## Memory benchmarking

For such small lists, memory should not be a problem, and we can assume that all these functions will use similar memory.

```python
>>> max_memories = [v["max_relative"] for v in (var_perf_memory, var_perf_2_memory, var_perf_3_memory, var_perf_4_memory)] 
>>> all(memory >= .99 and memory < 1.03 for memory in max_memories)
True

```

All functions use more or less the same memory:

```python
# for i in (var_perf, var_perf_2, var_perf_3, var_perf_4):
#     pt.pp(i["memory"]["max"])
17.57
17.58
17.58
17.6
```


## Longer list

So, for a short list, all the four functions used very similar memory. This, however, can change for a longer list:

```python
>>> x_long = x_short * 20
>>> for f in (variance, variance_2, variance_3, variance_4):
...    pt.config.set(f, "time", number=2, repeat=1) # you can use bigger values in your tests

```

### Time benchmarking

```python
>>> var_perf_time = pt.time_benchmark(variance, x_long)
>>> var_perf_2_time = pt.time_benchmark(variance_2, x_long)
>>> var_perf_3_time = pt.time_benchmark(variance_3, x_long)
>>> var_perf_4_time = pt.time_benchmark(variance_4, x_long)

>>> times2 = [
...     var_perf_time["min"],
...     var_perf_4_time["min"],
...     var_perf_3_time["min"]
... ]
>>> is_sorted(times2, reverse=True)
True

```

(In the test above, we did not use `var_perf_2`, as from time to time it is quicker than `var_perf_3`.)

Here, the point is not only in the ordering. Most interesting is that `variance()` is at least 100 slower than the other three versions - let's compare it to the qucikest version, `variance_3()`:

```python
>>> var_perf_time["min"] / var_perf_3_time["min"] > 100
True

```

In my machine, actually, `variance_3()` was almost 400 quicker than `variance()`:

```python
# for i in (var_perf, var_perf_2, var_perf_3, var_perf_4):
#     pt.pp(i["time"]["min"])
6.532
0.01861
0.01676
0.02086

```


As before, you can see the results in [this file](results_of_floats.md).


### Memory benchmarking

Another interesting thing is that `variance_4()`, despite using generators, used a little more memory than the other three functions. This is likely because of using three generators:

```python
# for i in (var_perf_memory, var_perf_2_memory, var_perf_3_memory, var_perf_4_memory):
#     pt.pp(i["max"])
18.44
18.44
18.86
19.45

```

You can conduct the same experiment with lists of `10_000_000` elements, and you will see quite a difference. As such an experiment would take too much time for testing purposes, we  do not include it here.
