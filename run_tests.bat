:: Run all doctests
echo Grab a cup of coffee as this will take some time, my friend...

python -m doctest README.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS

cd ./perftester
python perftester.py

cd ../docs
python -m doctest benchmarking_against_another_function.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
python -m doctest most_basic_use_time.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
python -m doctest use_of_config.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
python -m doctest most_basic_use_memory.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
python -m doctest README.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
python -m doctest use_case_raw_time_testing.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
python -m doctest change_benchmarking_function.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS

cd ../tests
python -m doctest doctest_function_str.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
python -m doctest doctest_function_floats.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
python -m doctest doctest_config.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
python -m doctest doctest_test_sum.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS
python -m doctest doctest_cache.md -o IGNORE_EXCEPTION_DETAIL -o NORMALIZE_WHITESPACE -o ELLIPSIS

cd ..
