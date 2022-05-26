# Case study: Tests of the built-in sum function

Catch exceptions:

```python
>>> import perftest as pt
>>> pt.time_test(sum, (None, None), "this cannot be summed up")
Traceback (most recent call last):
    ...
perftest.perftest.FunctionError: The tested function raised TypeError: unsupported operand type(s) for +: 'int' and 'str'

>>> pt.memory_usage_test(sum, (None, None), "this cannot be summed up")
Traceback (most recent call last):
    ...
perftest.perftest.FunctionError: The tested function raised TypeError: unsupported operand type(s) for +: 'int' and 'str'

>>> pt.benchmark(sum, "this cannot be summed up")
Traceback (most recent call last):
    ...
perftest.perftest.FunctionError: The tested function raised TypeError: unsupported operand type(s) for +: 'int' and 'str'

```

Make benchmarks:

```python
>>> n_of_test_repeats = 3 # how many times to conduct each test
>>> sum_perf_twice = {}
>>> n_set = 10, 20, 30, 100, 1000, 
>>> sum_twice = lambda x: sum(x) + sum(x)
>>> for n in n_set:
...    sum_perf_twice[n] = pt.benchmark(sum_twice, range(n))
>>>  


```

Running the same function (here, `sum`) twice will always take more time than running it only once.


### Time performance testing

If you run the function `sum` once, you will do it quicker than when you do it twice:

```python
>>> for n in n_set:
...    for _ in range(n_of_test_repeats):
...        pt.time_test(
...            sum,
...            pt.limits(sum_perf_twice[n]["time"]["min"], None),
...            range(n)
...        )

```

### Memory performance testing

In terms of memory, this should not have any effect, so clearly one of the below tests should not pass:

```python
>>> for n in n_set:
...    for _ in range(n_of_test_repeats):
...        pt.memory_usage_test(
...            sum,
...            pt.limits(sum_perf_twice[n]["memory"]["max"], None),
...            range(n)
...        ) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.MemoryTestError: Memory test not passed for function sum:
memory_limit = ...
maximum memory usage = ...

```
