# Does `cache` decorator affect RAM memory use?

> Of course it **should not**, but let's check it because why not.

Let's check out the `@cache` decorator from `functools`. As it is available from Python 3.9, we will use `@lru_cache`, available also in earlier versions of Python 3. We will use the standard function for such examples, that is, factorial:

```python
>>> import perftest as pt
>>> from functools import lru_cache
>>> def factorial(n):
...     return n * factorial(n - 1) if n else 1

>>> @lru_cache
... def factorial_cached(n): factorial(n)

```

Let's benchmark both functions:

```python
>>> no_cache = pt.benchmark(factorial, 100)
>>> with_cache = pt.benchmark(factorial_cached, 100)

```

Definitely, and as expected, the cached version takes a lot less time:

```python
>>> no_cache["time"]["min"] / with_cache["time"]["min"] > 100
True

```

And as this the `@lru_cache` decorator does not use RAM but cache memory, we should not expect an increase RAM use - and indeed, the two functions did use similar RAM:


```python
>>> 1.01 > no_cache["memory"]["max"] / with_cache["memory"]["max"] > 0.99
True

```

Certainly, the higher the `n` value, the greater the gain in speed, as the more results will be kept in cache.


## All results

All the results from my machine are shown below:

```python
## pt.pp(no_cache)
{'memory': {'max': 17.32,
            'max_relative': 1.005,
            'max_result_per_run': [17.32],
            'max_result_per_run_relative': [1.005],
            'mean': 17.32,
            'mean_result_per_run': [17.32],
            'raw_results': [[17.32, 17.32, 17.32]],
            'relative_results': [[1.005, 1.005, 1.005]]},
 'time': {'raw_times': [1.27e-05, 1.275e-05, 1.248e-05, 1.206e-05, 1.538e-05],
          'raw_times_relative': [155.8, 156.4, 153.1, 147.9, 188.6],
          'max': 1.538e-05,
          'mean': 1.307e-05,
          'min': 1.206e-05,
          'min_relative': 147.9}}

## pt.pp(with_cache)
{'memory': {'max': 17.33,
            'max_relative': 1.005,
            'max_result_per_run': [17.33],
            'max_result_per_run_relative': [1.005],
            'mean': 17.33,
            'mean_result_per_run': [17.33],
            'raw_results': [[17.33, 17.33, 17.33]],
            'relative_results': [[1.005, 1.005, 1.005]]},
 'time': {'raw_times': [1e-07, 9.766e-08, 9.825e-08, 1.088e-07, 1.325e-07],
          'raw_times_relative': [1.221, 1.192, 1.199, 1.327, 1.617],
          'max': 1.325e-07,
          'mean': 1.074e-07,
          'min': 9.766e-08,
          'min_relative': 1.192}}

```
