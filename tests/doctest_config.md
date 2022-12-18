# Tests of the `config` instance

You can read how to use `pt.config` [here](../docs/use_of_config.md). Below, you will find abundant unit tests, most of which would be unnecessary in the mentioned documentation file, also because some of them may seem repetitive (but are needed).


## Defaults

```python
>>> import perftester as pt
>>> pt.config.defaults
{'time': {'number': 100000, 'repeat': 5}, 'memory': {'repeat': 1}}

>>> original_defaults = pt.config.defaults
>>> pt.config.set_defaults("time", Number=100)
>>> pt.config.defaults
{'time': {'number': 100, 'repeat': 5}, 'memory': {'repeat': 1}}

>>> pt.config.set_defaults("time", Repeat=20)
>>> pt.config.defaults
{'time': {'number': 100, 'repeat': 20}, 'memory': {'repeat': 1}}
>>> pt.config.set_defaults("time", Repeat=2, Number=7)
>>> pt.config.defaults
{'time': {'number': 7, 'repeat': 2}, 'memory': {'repeat': 1}}

>>> pt.config.set_defaults("memory", Repeat=100)
>>> pt.config.defaults
{'time': {'number': 7, 'repeat': 2}, 'memory': {'repeat': 100}}

>>> pt.config.set_defaults("memory", Number=100)
Traceback (most recent call last):
    ...
perftester.perftester.IncorrectArgumentError: For memory tests, you can only set repeat, not number.

>>> pt.config.set_defaults("memory", Number=100, Repeat=5)
Traceback (most recent call last):
    ...
perftester.perftester.IncorrectArgumentError: For memory tests, you can only set repeat, not number.

>>> pt.config.set_defaults("memory", Repeat=5, Number=100)
Traceback (most recent call last):
    ...
perftester.perftester.IncorrectArgumentError: For memory tests, you can only set repeat, not number.

>>> pt.config.defaults = original_defaults

```

## Actual settings

```python
>>> def f(): pass
>>> pt.config.set(f, "time", Number=20, Repeat=10)
>>> pt.config.settings[f]
{'memory': {'repeat': 100}, 'time': {'number': 20, 'repeat': 10}}

>>> pt.config.set(f, "time", Number=50)
>>> pt.config.settings[f]
{'memory': {'repeat': 100}, 'time': {'number': 50, 'repeat': 10}}

>>> pt.config.set(f, "time", Repeat=5)
>>> pt.config.settings[f]
{'memory': {'repeat': 100}, 'time': {'number': 50, 'repeat': 5}}

>>> pt.config.set(f, "memory", Repeat=5)
>>> pt.config.settings[f]
{'memory': {'repeat': 5}, 'time': {'number': 50, 'repeat': 5}}

>>> pt.config.set(f, "memory", Number=5)
Traceback (most recent call last):
    ...
perftester.perftester.IncorrectArgumentError: For memory tests, you can only set repeat, not number.

>>> pt.config.set(f, "memory", Number=5, Repeat=10)
Traceback (most recent call last):
    ...
perftester.perftester.IncorrectArgumentError: For memory tests, you can only set repeat, not number.

```

## Incorrect which argument

```python
>>> pt.config.set(f, "memorys", Repeat=5)
Traceback (most recent call last):
    ...
perftester.perftester.IncorrectArgumentError: Argument which must be str from among memory, time
>>> pt.config.set(f, "times", Repeat=5)
Traceback (most recent call last):
    ...
perftester.perftester.IncorrectArgumentError: Argument which must be str from among memory, time
>>> pt.config.set_defaults(f, "memorys", Repeat=5)
Traceback (most recent call last):
    ...
perftester.perftester.IncorrectArgumentError: Argument which must be str from among memory, time
>>> pt.config.set_defaults(f, "times", Repeat=5)
Traceback (most recent call last):
    ...
perftester.perftester.IncorrectArgumentError: Argument which must be str from among memory, time

```

## `.digits_for_printing` and `pp()`

```python
>>> pt.config.digits_for_printing
4
>>> pt.pp([1.2, 1.55555555])
[1.2, 1.556]
>>> pt.config.digits_for_printing = 7
>>> pt.pp([1.2, 1.55555555])
[1.2, 1.555556]


```

## Singleton

The `pt.Config` is defined as a singleton, so in one session, you cannot create more than one its instance:

```python
>>> another_config = pt.Config()
>>> id(another_config) ==  id(pt.config)
True
>>> another_config is pt.config
True

```

As you see, no exception is raises, but you simply have two names (`pt.config` and `another_config`) that link to the same object.