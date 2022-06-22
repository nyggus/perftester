# Basic use of `perftester.time_test()`

```python
>>> import perftester as pt
>>> def preprocess(string):
...    return string.lower().strip()
>>> test_string = "  Oh oh the young boy, this YELLOW one, wants to sing a song about the sun.\n"
>>> preprocess(test_string)[:19]
'oh oh the young boy'

```

## First step - checking performance

We will first benchmark the function, to learn how it performs:

```python
>>> first_run = pt.time_benchmark(preprocess, string=test_string)

```

`first_run` gives the following results:

```python
# pt.pp(first_run)
{'raw_times': [2.476e-07, 2.402e-07, 2.414e-07, 2.633e-07, 3.396e-07],
 'raw_times_relative': [3.325, 3.226, 3.242, 3.536, 4.56],
 'max': 3.396e-07,
 'mean': 2.664e-07,
 'min': 2.402e-07,
 'min_relative': 3.226}
```

Fine, no need to change the settings, as the raw times are rather short, and the relative time ranges from 3.3 to 4.6.


# Raw time testing

We can define a simple time-performance test, using raw values, as follows:

```python
>>> pt.time_test(preprocess, raw_limit=2e-06, string=test_string)

```

As is with the `assert` statement, no output means that the test has passed.

If you overdo with the limit so that the test fails, you will see the following:

```python
>>> pt.time_test(preprocess, raw_limit=2e-08, string=test_string) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftester.perftester.TimeTestError: Time test not passed for function preprocess:
raw_limit = 2e-08
minimum run time = ...

```


# Relative time testing

Alternatively, we can use relative time testing, which will be more or less independent of a machine on which it's run:

```python
>>> pt.time_test(preprocess, relative_limit=10, string=test_string)

```

If you overdo with the limit so that the test fails, you will see the following:

```python
>>> pt.time_test(preprocess, relative_limit=1, string=test_string) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftester.perftester.TimeTestError: Time test not passed for function preprocess:
relative_limit = 1
minimum time ratio = ...

```

# Both raw and relative testing

We can combine the two types of tests:

```python
>>> pt.time_test(preprocess, raw_limit=2e-06, relative_limit=10, string=test_string)

```

Again, here're three examples of a failed test:


```python
>>> pt.time_test(preprocess, raw_limit=2e-08, relative_limit=10, string=test_string) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftester.perftester.TimeTestError: Time test not passed for function preprocess:
raw_limit = 2e-08
minimum run time = ...

>>> pt.time_test(preprocess, raw_limit=2e-06, relative_limit=1, string=test_string) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftester.perftester.TimeTestError: Time test not passed for function preprocess:
relative_limit = 1
minimum time ratio = ...

>>> pt.time_test(preprocess, raw_limit=2e-08, relative_limit=1, string=test_string) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftester.perftester.TimeTestError: Time test not passed for function preprocess:
raw_limit = 2e-08
minimum run time = ...

```

As you see from the last example, you will not learn if both the raw and the relative tests fail. This is because the tests are performed laizily, and if the first (which is the raw one) fails than an exception is immediately raised.

# Conclusion

Many a time, this will be enough for you to perform time-based performance tests, which you can do in `pytest`s or `doctest`s, but most of all, as an independent testing framework. In [another file](most_basic_use_memory.md), you can learn how to perform a time-based performance test relative to another function.
