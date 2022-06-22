# Use `perftester` as CLI

This is a similar approach that `pytest` takes. You simply run `perftester` in a directory of your choice and wait for the results. In the meantime, `perftester` will collect all the testing modules (which start with "perftester_" and have ".py" extension), then it will collect all `perftester` functions in each module (they start with "perftester_"), and then it will run all the functions. If you add any updates to `pt.config`, it will do the update. And that's it, you have the results printed to the console.

This approach uses the default state of `pt.config` object. You can change it before running the tests using the config_perftester.py Python script, which should be located in the directory from which you run the tests. That way, you can use multiple config_perftester.py, simply by putting them in different directories and running `perftester` from these directories.

> The config_perftester.py file is not that necessary, as you can change any settings directly in testing files. You can find examples [here](../tests/perftester_for_testing.py) and [here](tests/../../tests/for_testing/perftester_for_testing_2.py).


## Use `perftester` command for a directory

You can use `perftester` for a directory, by providing a path to it:

```shell
$ perftester ./tests/memory_tests/
```

`perftester` will look for config_perftester.py file in the directory in which you run the command, not in this provided directory. So, if you have a config file there, simply move to it and then run `perftester`.

`perftester` will recursively locate all `perftester_` testing modules, and will run all the `perftester` tests from them.


## Use `perftester` command for a single file

You can use `perftester` for a single file, by providing a path to this file:

```shell
$ perftester ./tests/perftester_time_tests.py
```

Remember that when you do so, `perftester` will look for config_perftester.py file.


## Use `perftester` command without a path

If you ommit a path to the command, that is,

```shell
$ perftester
```

this will be the same as running the command with a path to the current directory, so

```shell
$ perftester .
```


## Log results

When you use perftester as a CLI program, you can save the results to a file. 

> You cannot do that when you run `perftester` in a different way, like in an interactive session or with pytest. Of course, you can create then your own logger.

The default setting is to **not** log. In order to change that, you need to change `pt.config`'s attribute `log_to_file` to `True`, and provide a log file as `log_file`, e.g.

```python
pt.config.log_to_file = True
pt.config.log_file = pathlib.Path(".") / "perftester.log"

```

> You must do that in the config_perftester.py file, not elsewhere.
> 