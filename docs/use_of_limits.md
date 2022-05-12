# Use of `perftest.limits`

Function `time_test()` has argument `time_limits` (it defaults to `None`), and function `memory_usage_test()` has argument `memory_limits` (also defaults to `None`). These two arguments need to be provided as an instance of a namedtupe called `limits`, which is defined in` perftest`:

```python
>>> import perftest as pt
>>> pt.limits
<class 'perftest.perftest.limits'>

```

`limits` has two attributes only:

```python
>>> pt.limits._fields
('raw_limit', 'relative_limit')

```

As the field names suggest, the first one defines limits to be used in raw testing while the latter in relative testing, and this refers to both `time_test()` and `memory_test()`. 

You do not have to use them, since it's enough to provide a regular tuple:

```python
>>> def f(): return
>>> pt.time_test(f, pt.limits(10e-05, None))
>>> pt.time_test(f, (10e-05, None))

```

> While both examples work the same way, the `pt.limits` namedtuple is a preferred way of providing limits, as it increases code readability.

Note the below code, which uses a regular tuple:

```python
>>> def sum_of_powers(n, power): return sum(i**power for i in range(n))
>>> pt.time_test(f, (2, 275))
>>> pt.memory_usage_test(f, (18, 1.1))

```

For sure, this is concise, but it isn't readable. Let's use `pt.limits` to increase redability:

```python
>>> def sum_of_powers(n, power): return sum(i**power for i in range(n))
>>> time_limits = pt.limits(raw_limit=2, relative_limit=275)
>>> memory_limits = pt.limits(raw_limit=18, relative_limit=1.1)
>>> pt.time_test(f, time_limits)
>>> pt.memory_usage_test(f, memory_limits)

```

Of course, we can use one-liners to shorten the code:


```python
>>> def sum_of_powers(n, power): return sum(i**power for i in range(n))
>>> pt.time_test(f, pt.limits(raw_limit=2, relative_limit=275))
>>> pt.memory_usage_test(f, pt.limits(raw_limit=18, relative_limit=1.1))

```

This is still readable, and which is better of the two uses of `pt.limits` depends on the situation. We can go one step farther:

```python
>>> def sum_of_powers(n, power): return sum(i**power for i in range(n))
>>> pt.time_test(f, pt.limits(2, 275))
>>> pt.memory_usage_test(f, pt.limits(18, 1.1))

```

This version may look less readable, for for anyone using `perftest` from time to time, `pt.limits` will be readable itself, so no need to provide field names.