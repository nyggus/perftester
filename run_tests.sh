# Run all doctests
echo Grab a cup of coffee as this will take some time, my friend...

cd ./perftester
echo -- Docstrings in perftester.py
python perftester.py

cd ..
echo -- The main README.md
python -m doctest README.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS


cd ./docs
echo --- Documentation files - in the docs/ folder ---
echo -- docs/benchmarking_against_another_function.md
python -m doctest benchmarking_against_another_function.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- docs/most_basic_use_time.md
python -m doctest most_basic_use_time.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- docs/doctest use_of_config.md
python -m doctest use_of_config.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- docs/most_basic_use_memory.md
python -m doctest most_basic_use_memory.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- docs/README.md
python -m doctest README.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- docs/use_case_raw_time_testing.md
python -m doctest use_case_raw_time_testing.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- change_benchmarking_function.md
python -m doctest change_benchmarking_function.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- use_of_memory_tracker.md
python -m doctest use_of_memory_tracker.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS

cd ../tests
echo --- Unit test files - in the the tests/ folder ---
echo -- tests/doctest_function_str.md
python -m doctest doctest_function_str.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- tests/doctest_function_floats.md
python -m doctest doctest_function_floats.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- tests/doctest_config.md
python -m doctest doctest_config.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- tests/doctest_test_sum.md
python -m doctest doctest_test_sum.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
echo -- doctest_cache.md
python -m doctest doctest_cache.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS

cd ..