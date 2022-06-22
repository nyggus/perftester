# Basic use of `perftest.memory_usage_test()`

```python
>>> import perftest as pt
>>> def sum_of_squares(x):
...    return sum([i**2 for i in x])
>>> x = [1, 2, 10, ]
>>> sum_of_squares(x)
105

```

Yes, there is a minor (major?) mistake in the function, one that does not affect the result itself but the function's performance. We will return to it later.

## First step - checking performance

Let's run the function to learn how it performs. This will be more interesting with a long list, not such a short one as above:

```python
>>> x = x * 10_000_000
>>> sum_of_squares(x)
1050000000

```

First, note that memory tests, on default, are not repeated, as any function that has no random components will use the same amount of memory (or almost the same, variation being negligble). Memory tests thus has `repeat` of 1 and do not use `number`.

Let's run the function with `None` limits, to check its performance:

```python
>>> first_run = pt.memory_usage_benchmark(sum_of_squares, x)

```

`first_run` gives a lot of results, so let's not show them here - you can see them in this [file](results_most_basic_memory.md). Notice that the use of memory changes over time. For testing, let's check the maximum measures, through `first_run["max_result_per_run"]`; the result was `[474.76953125]`. 


# Raw memory usage testing

We can define a simple memory use test, using raw values, as follows:

```python
>>> pt.memory_usage_test(sum_of_squares, raw_limit=800, x=x)

```

If you overdo with the limit (below, we will expect 10 instead of 500) so that the test fails, you will see the following:

```python
>>> pt.memory_usage_test(sum_of_squares, raw_limit=10, x=x) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.MemoryTestError: Memory test not passed for function sum_of_squares:
memory_limit = 10
maximum memory usage = ...

```


# Relative memory testing

Alternatively, we can use relative memory testing, which will be more or less independent of a machine on which it's run:

```python
>>> pt.memory_usage_test(sum_of_squares, relative_limit=40, x=x)

```

If you overdo with the limit so that the test fails, you will see the following:

```python
>>> pt.memory_usage_test(sum_of_squares, relative_limit=1, x=x) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.MemoryTestError: Memory test not passed for function sum_of_squares:
relative memory limit = 1
maximum obtained relative memory usage = ...

```

# Both raw and relative testing

And we can combine the two types of tests:

```python
>>> pt.memory_usage_test(sum_of_squares, raw_limit=700, relative_limit=40, x=x)

```

Again, here're three examples of a failed test:

```python
>>> pt.memory_usage_test(sum_of_squares, raw_limit=10, relative_limit=40, x=x) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.MemoryTestError: Memory test not passed for function sum_of_squares:
memory_limit = 10
maximum memory usage = ...

>>> pt.memory_usage_test(sum_of_squares, raw_limit=10, relative_limit=1, x=x) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.MemoryTestError: Memory test not passed for function sum_of_squares:
memory_limit = 10
maximum memory usage = ...

>>> pt.memory_usage_test(sum_of_squares, raw_limit=10, relative_limit=1, x=x) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.MemoryTestError: Memory test not passed for function sum_of_squares:
memory_limit = 10
maximum memory usage = ...

```

As you see from the last example, you will not learn if both the raw and the relative tests fail. This is because the tests are performed laizily, and if the first (which is the raw one) fails than an exception is immediately raised.


# Refactorization of `sum_of_squares`

As we mentioned before, `sum_of_squares` is not perfect. We did a small mistake in its definition that did not affect the results but did affect the function's performance. This is because `sum()` does not require us to pass a list to it, but we can instead pass a generator. Note:

```python
>>> sum([i for i in range(100)]) == sum(i for i in range(100))
True

```

Our refactored function will be as follows:

```python
>>> def sum_of_squares_refactored(x):
...    return sum(i**2 for i in x)

```

Now, let's see how it performs:

```python
>>> refactored_performance = pt.memory_usage_benchmark(sum_of_squares_refactored, x=x)
>>> refactored_performance["max"] < first_run["max"] # so memory use after refactoring will be smaller
True

```

# Conclusion

What you've seen is the most basic use of `perftest.memory_usage_test()`, but it will be enough for most use cases. You can learn more advanced uses throughout the documentation in this folder, from the main README, and from the [tests folder](../tests/).