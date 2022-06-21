# Tests of the `perftest` package

The `perftest` package uses only the `doctest` framework for unit testing. As testing here is fairly straightforward, we do not need any complex unit testing tools, such as mocking or randomized testing. (In fact, you can use both in `doctest`, though the readability could slightly suffer from that.)

> The use of `doctest`ing as the only testing framework in `perftest` is an experiment. Tests in `perftest` are abundant, and are collected in four locations: [the main README](../README.md), docstrings in [the main perftest module](../perftest/perftest.py), [the docs folder](../docs/), and [this folder](./).

`doctest`ing joins two functions: testing and documentation. This can be seen in [README](../README.md), in which `doctest`s mainly help to keep the examples up-to-date. The documentation files in [the docs folder](../docs/) are more wordy, as the documentation function has a higher priority in them. Here, however, testing is more important, so these files are not that wordy, and their main purpose is testing.

Initially, [the docs folder](../docs/) contained Markdown files while [the tests folder](./) contained text files (as text files are also a good way of writing doctests). However, it quickly occurred that Markdown files are a little more readable, especially in a browser, so all testing files are now formatted using Markdown. The testing files here, however, has much less explanation, limited mainly to explanation helping the reader understand the tests or some of their aspects.