# `perftest.time_test()`: A use case of raw time testing

Sometimes it makes sense to perform raw time testing. Imagine you have an app installed in a production environment, and you make some minor changes to the code. You do not expect them to affect the execution time - and maybe you even must ensure that some time limit will not be broken.

Other times, you may want to conduct such performance testing without any changes to the code: remember that performance testing tests not only the app/function itself, but also the environment in which the app runs. If the machine is suffering for far too many processes run simultaneously, it is possible that your process will take much more time than normally; you can use `perftest` to check that.

In such cases, using raw performance testing makes much sense. Hence, `perftest` offers both types of testing, and the developer will have to choose which is a right choice in a particular situation, in some situations raw benchmarking while in others relative benchmarking being a better choice. You can always use both.


## Use case

Let's assume we are not interested in memory-use performance tests, just in time-related tests. This is the function we have implemented:

```python
>>> from time import sleep
>>> def f(x, y):
...    sleep(0.1) # to emulate some processing of x and y
...    return x + y

```

We already know that the function should take only a little above one-ten of a second, but for the moment let's forget it - although we can assume that the function needs some time to perform, not just milliseconds. Let's run some benchmarks.

The first step is import `perftest`:

```python
>>> import perftest as pt

```

This creates object `pt.config`, which all `perftest` functions use, and which you can use to change (or check) settings. We will use `config` to decrease the number of runs of the function, as with the default million of runs we would have to wait way too long:

```python
>>> pt.config.set(f, "time", repeat=3, number=5)

```


In real life, you will seldom want to run the function five times (actually, fifteen times, as we have three repeats), but we do it here for the sake of doctests (to make them short enough). First, we need to check how much time this can take:

```python
>>> f_time_performance = pt.time_benchmark(f, x=10, y=10)

```

Remmeber that in many situations, performance will strongly depend on a function's arguments; in our case, we know this is not the case. You can see the performance using `pt.pp(f_time_performance)`. In my machine, I got the following performance:

```python
{'raw_times': [0.1006, 0.1005, 0.1008],
 'raw_times_relative': [1375000.0, 1374000.0, 1378000.0],
 'max': 0.1008,
 'mean': 0.1007,
 'min': 0.1005,
 'min_relative': 1374000.0}
```

For raw testing, what counts is `"min"`, as in `timeit.timeit()` and `timeit.repeat()`; it is indeed taken as the actual result of the test. 

> Remember that the raw results from `time.test()` are not the same as those from `timeit` functions; `perftest` reports raw results *per function call* while `timeit` functions per all function calls.

We can safely expect that `f()` should not take much more than `0.1`. For many functions, we should be less strict with defining time limits, as the results can vary much more than those in our case, and can depend on the environment in which they are run. For `f()`, the small variation results from the definition of the function, which simply sleeps for 0.1 sec.

So, we're ready to build our tests:

```python
>>> pt.time_test(f, raw_limit=0.121, x=10, y=10)

```
