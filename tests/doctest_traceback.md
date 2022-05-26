# Manipulating the traceback

The default behavior of `perftest` is to **not** incluide the full traceback when a test does not pass. This is because when running performance tests, you're not interested in finding bugs, and this is what traceback is for. Instead, you want to see which test did not pass and how.

> You will **not** see any difference in the below `doctest`s, but you will notice the difference in the length of the output of actual tests that do not pass. You will see, however, the actual output below, but not in the `doctest`s.


```python
>>> import perftest as pt
>>> raise pt.TimeTestError
Traceback (most recent call last):
    ...
perftest.perftest.TimeTestError

>>> pt.config.full_traceback()
>>> raise pt.TimeTestError
Traceback (most recent call last):
    ...
perftest.perftest.TimeTestError

>>> pt.config.cut_traceback()
>>> raise pt.TimeTestError
Traceback (most recent call last):
    ...
perftest.perftest.TimeTestError

```

```python
>>> import time
>>> def f(): time.sleep(.1)
>>> pt.config.set(f, "time", number=1, repeat=1)
>>> pt.time_test(f, (.001, None)) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.TimeTestError: Time test not passed for function f:
raw_limit = ...
minimum run time = ...

>>> pt.config.full_traceback()
>>> pt.time_test(f, (.001, None)) #doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
perftest.perftest.TimeTestError: Time test not passed for function f:
raw_limit = ...
minimum run time = ...

```

And this is the actual output you would see in your console; I removed most of the paths, and of course, you could get a slightly different `minimum run time`:

```python
# pt.time_test(f, (.001, None))
perftest.perftest.TimeTestError: Time test not passed for function f:
raw_limit = 0.001
minimum run time = 0.10100129999773344
```

```python
# pt.config.full_traceback()
# pt.time_test(f, (.001, None))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File .../perftest.py", line 510, in time_test
    check_if(
  File ".../site-packages/easycheck-0.3.1-py3.8.egg/easycheck/easycheck.py", line 114, in check_if
    _raise(handle_with, message)
  File ".../site-packages/easycheck-0.3.1-py3.8.egg/easycheck/easycheck.py", line 848, in _raise
    raise error(message)
perftest.perftest.TimeTestError: Time test not passed for function f:
raw_limit = 0.001
minimum run time = 0.10065620000023046
```
