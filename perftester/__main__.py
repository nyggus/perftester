"""Module responsible for the CLI perftester command."""
import importlib
import inspect
import os
import pathlib
import sys
from collections import namedtuple
from easycheck import check_if_paths_exist
from perftester import config, TimeTestError, MemoryTestError, CLIPathError


TestResults = namedtuple("TestResults", "passed_tests failed_tests")

config.full_traceback()


def main():
    files = _read_cli_args()
    _initialize_log_file(len(files))
    _import_settings_from_config_file()
    passed_perftesters, failed_perftesters = [], []

    for file in files:
        module, module_name = _import_module(file)
        perftester_functions = _find_perftester_functions(module)
        for func in perftester_functions:
            this_test = _perftester(module_name, func)
            if this_test:
                failed_perftesters.append(
                    f"{str(module_name)}.{func.__name__}"
                )
            else:
                passed_perftesters.append(
                    f"{str(module_name)}.{func.__name__}"
                )

    test_results = TestResults(
        passed_tests=passed_perftesters, failed_tests=failed_perftesters
    )
    _log_perftester_results(test_results)


def _read_cli_args():
    if len(sys.argv) == 1:
        path = pathlib.Path(os.getcwd())
    else:
        # sys.argv[1] is always a string, so no need to check it
        path = pathlib.Path(sys.argv[1])
    check_if_paths_exist(
        path,
        CLIPathError,
        "Incorrent path provided with perftester CLI command",
    )
    if path.is_dir():
        files = _find_perftester_files(path)
    elif path.is_file:
        files = [
            path,
        ]
    else:
        raise CLIPathError(
            f"Unexpected problem with path {path}, please double check"
        )
    return files


def _log(message):
    print(message)
    if config.log_to_file:
        try:
            with open(config.log_file, "a") as f:
                f.write(message + "\n")
                f.flush()
        except OSError as e:
            print(
                f"Error in writing to {config.log_file}: {e}. "
                "perftester log will not be saved there."
            )
            config.log_to_file = False


def _import_settings_from_config_file():
    settings_file = config.config_file
    if settings_file.exists():
        sys.path.append(str(settings_file.parent.absolute()))
        importlib.import_module("config_perftester")
        _log(f"Importing settings from {settings_file}.")
    else:
        _log(
            "No settings file detected, using default perftester configuration."
        )


def _initialize_log_file(files_len):
    if config.log_to_file:
        try:
            with open(config.log_file, "w") as f:
                f.write("")
        except OSError as e:
            print(
                f"Error in writing to {config.log_file}: {e}. "
                "perftester log will not be saved there."
            )
            config.log_to_file = False

    _log(
        "Performance tests using perftester\n"
        "perftester: https://github.com/nyggus/perftester\n"
        "--------------------------------------------"
        f"\n\nCollected {files_len} "
        f"perftester module{'s' if files_len > 1 else ''} for testing.\n"
    )


def _import_module(file):
    path_str = str(file.parent.absolute())
    if path_str not in sys.path:
        sys.path.append(path_str)
    module_name = file.name[:-3]
    module = importlib.import_module(module_name)
    return module, module_name


def _perftester(module_name, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except TimeTestError as e:
        _log(f"\nTimeTestError in {module_name}.{func.__name__}\n{e}")
        return 1
    except MemoryTestError as e:
        _log(f"\nMemoryTestError in {module_name}.{func.__name__}\n{e}")
        return 1
    except Exception as e:
        _log(
            "\nUnexpected error in test function "
            f"{module_name}.{func.__name__}\n{e}\n"
        )
        return 1
    return 0


def _find_perftester_functions(module):
    functions = []
    items = dir(module)
    for item in items:
        item_real = getattr(module, item)
        if inspect.isfunction(item_real) and item.startswith("perftester_"):
            functions.append(item_real)
    return functions


def _find_perftester_files(path: pathlib.Path):
    return [file for file in path.rglob("perftester_*.py")]


def _log_perftester_results(test_results):
    passed_perftesters = test_results.passed_tests
    failed_perftesters = test_results.failed_tests
    n_of_tests = len(passed_perftesters) + len(failed_perftesters)

    _log(
        f"\n\nPerfomance testing done.\nOut of {n_of_tests} tests,"
        f" {len(passed_perftesters)} has passed"
        f" and {len(failed_perftesters)} has failed."
    )
    if len(passed_perftesters) > 0:
        _log("\nPassed tests:")
        for test in passed_perftesters:
            _log(test)
    if len(failed_perftesters) > 0:
        _log(f"\nFailed tests:")
        for test in failed_perftesters:
            _log(test)
    print()


if __name__ == "__main__":
    main()
