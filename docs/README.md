# `perftester`: documentation

This folder contains a number of files that serve two functions: documentation and testing. The main [README](../README.md) contains basic information about how to use `perftester`, while this folder collects both basic and more advanced knowledge of using the package. All these files serve also as doctests (`doctest` being the only testing framework used in `perftester`).

The knowledge is collected in the following files:
* [Basic use of `time_test()`](most_basic_use_time.md)
* [Basic use of `memory_usage_test()`](most_basic_use_memory.md)
* [Using `perftester.config` for advanced performance testing](use_of_config.md)
* [Using `perftester` for simple benchmarking, and for performance testing a function relative to the performance of another function](benchmarking_against_another_function.md)
* [Use case of raw time testing](use_case_raw_time_testing.md)
* [Changing a built-in benchmarking function](change_benchmarking_function.md)
* [Use of the `perftester.pp()` function](use_of_pp.md)
* [Use of `perftester` as a command-line testing framework](use_perftester_as_CLI.md)

You can also read the test files, located in [the tests folder](../tests/).