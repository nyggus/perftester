# Case study: Tests of the built-in sum function

Catch exceptions:

```python
>>> import perftester as pt
>>> pt.time_test(sum, "this cannot be summed up", raw_limit=1)
Traceback (most recent call last):
    ...
perftester.perftester.FunctionError: The tested function raised TypeError: unsupported operand type(s) for +: 'int' and 'str'

>>> pt.memory_usage_test(sum, "this cannot be summed up", raw_limit=1)
Traceback (most recent call last):
    ...
perftester.perftester.FunctionError: The tested function raised TypeError: unsupported operand type(s) for +: 'int' and 'str'

>>> pt.time_benchmark(sum, "this cannot be summed up")
Traceback (most recent call last):
    ...
perftester.perftester.FunctionError: The tested function raised TypeError: unsupported operand type(s) for +: 'int' and 'str'

>>> pt.memory_usage_benchmark(sum, "this cannot be summed up")
Traceback (most recent call last):
    ...
perftester.perftester.FunctionError: The tested function raised TypeError: unsupported operand type(s) for +: 'int' and 'str'

```

Make benchmarks:

```python
>>> n_of_test_repeats = 3 # how many times to conduct each test
>>> time_sum_perf_twice = {}
>>> memory_sum_perf_twice = {}
>>> n_set = 10, 20, 30, 100, 1000, 
>>> sum_twice = lambda x: sum(x) + sum(x)
>>> for n in n_set:
...    time_sum_perf_twice[n] = pt.time_benchmark(sum_twice, range(n))
...    memory_sum_perf_twice[n] = pt.memory_usage_benchmark(sum_twice, range(n))
>>>  


```

Running the same function (here, `sum`) twice will always take more time than running it only once.


### Time performance testing

If you run the function `sum` once, you will do it quicker than when you do it twice:

```python
>>> for n in n_set:
...    for _ in range(n_of_test_repeats):
...        pt.time_test(sum,
...                     range(n),
...                     raw_limit=time_sum_perf_twice[n]["min"])

```

### Memory performance testing

In terms of memory, this should not have any effect, as both functions should use its same amount. So none of the below tests should fail:

```python
>>> for n in n_set:
...    for _ in range(n_of_test_repeats):
...        pt.memory_usage_test(sum,
...                             range(n),
...                             raw_limit=memory_sum_perf_twice[n]["max"]*1.1) 

```
