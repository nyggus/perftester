# Use of `pt.pp()` function

`perftest` offers a `pp()` function for pretty-printing of benchmarking results. This is a simple wrapper around the built-in `pprint.pprint()` function that uses `rounder.signif_object()` function (see [here](https://pypi.org/project/rounder/) to learn about the `rounder` package).

The `pp()` function is not included here for more general uses (even if it can be used in man y various scenarios), as it depends on `pt.config` through the `pt.config.digits_for_printing` attribute. If you want to achieve similar effects without the need to import `perftest`, use the `rounder` package to round objects and `pprint.pprint()` to pretty-print them.

Throughout the documentation files in this repository, you will find many examples of using `pt.pp()` to print the results of various benchmarks and tests. Thus, here you will find only several simple uses of `pt.pp()`.

```python
>>> import perftest as pt
>>> pt.pp(20.00444)
20.0
>>> pt.pp(.00444)
0.00444
>>> pt.pp(.00444444444)
0.004444

```

A more complex example:

```python
>>> pt.pp(
...     {"a": 20.00004, "b": 0.00444444},
...     [1.1233333, 123123123123.0002, "Shout Bamalama!"]
... )
{'a': 20.0, 'b': 0.004444}
[1.123, 123100000000.0, 'Shout Bamalama!']

```

As written above, you cannot directly change the behavior of `pt.pp()`, but you can do so using `pt.config.digits_for_printing`:

```python
>>> pt.config.digits_for_printing = 7
>>> pt.pp(
...     {"a": 20.00004, "b": 0.00444444},
...     [1.1233333, 1231.1212, "Shout Bamalama!"]
... )
{'a': 20.00004, 'b': 0.00444444}
[1.123333, 1231.121, 'Shout Bamalama!']

```
