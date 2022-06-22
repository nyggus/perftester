# Overwriting the built-in benchmarking function

You can overwrite the built-in benchmark function, which is stored as `pt.config.benchmark_function`. That way, you can, for instance, benchmark one function against another function. 

> Do remember, however, that this approach changes the benchmark function in all the tests that will follow in the same session.

> **In most uses, avoid overwriting the built-in benchmarking function**. `perftester` enables you to do that, but does not offer (for purpose!) any additional functionalities related to this approach. When you want to benchmark one function against another one, you can do so in a more `perftester`ic way, described [here](benchmarking_against_another_function.md). We describe it here only because it is possible, so it's better to show it and warn you to use this approach only when you **really** need to do this. One example is when you want to benchmark many functions against this one particular function. In that case, it makes sense to follow the approach described below.

## How-to

Imagine we have the following function we want to test (we've used it before):

```python
>>> def square_of_sum(x): return sum(x)**2

```

We know it should be quicker than this function:

```python
>>> def sum_of_squares(x): return sum(i**2 for i in x)

```

We can bechmark the two functions one against another as described in [this file](benchmarking_against_another_function.md), but here, we will, instead, overwrite the built-in function. First, let's run memory benchmarks using the built-in function (you don't have to do this — we do it for explanation purposes):

```python
>>> import perftester as pt
>>> x = [1.0002, 56.0303, 780, 0.1, 445.55553, 190.01, 56.76]*10_000_000
>>> first_bench = pt.memory_usage_benchmark(sum_of_squares, x=x)
>>> first_bench["max_relative"] > 25
True

```

Now, let's overwrite the built-in benchmark function:

```python
>>> pt.config.benchmark_function = lambda: sum_of_squares(x)
>>> pt.config.reload_memory()
>>> pt.config.reload_time()

```

Had `sum_of_squares()` taken no arguments, we would have not needed the `lambda` function, just the function itself. However, as it takes an argument `x`, we need to do this trick. `perftester` does not enable you to pass arguments to an overwritten benchmarking function, for a simple reason that you should rather avoid overwriting it.

> Note that, theoretically, we did not have to reload the benchmarks stored in `config`, since they would be reloaded before any benchmark or test; however, if you do not do that, you would get incorrect values after looking at `pt.config.memory_benchmark` and `pt.config.time_benchmark`. 

We are ready to perform our tests:

```python
>>> second_bench = pt.memory_usage_benchmark(sum_of_squares, x=x)
>>> second_bench["max_relative"] < 1.01
True
>>> first_bench["max_relative"] > second_bench["max_relative"]
True

```
