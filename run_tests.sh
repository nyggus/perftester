# Run all doctests
echo Grab a cup of coffee as this will take some time, my friend...

cd ./perftest
echo -- Docstrings in perftest.py
python -m doctest perftest.py

cd ..
echo -- The main README.md
python -m doctest README.md 


cd ./docs
echo --- Documentation files - in the docs/ folder ---
echo -- docs/benchmarking_against_another_function.md
python -m doctest benchmarking_against_another_function.md
echo -- docs/most_basic_use_time.md
python -m doctest most_basic_use_time.md
echo -- docs/doctest use_of_config.md
python -m doctest use_of_config.md
echo -- docs/most_basic_use_memory.md
python -m doctest most_basic_use_memory.md
echo -- docs/README.md
python -m doctest README.md
echo -- docs/use_case_raw_time_testing.md
python -m doctest use_case_raw_time_testing.md
echo -- docs/use_of_limits.md
python -m doctest use_of_limits.md
echo -- change_benchmarking_function.md
python -m doctest change_benchmarking_function.md

cd ../tests
echo --- Unit test files - in the the tests/ folder ---
echo -- tests/doctest_function_str.md
python -m doctest doctest_function_str.md
echo -- tests/doctest_function_floats.md
python -m doctest doctest_function_floats.md
echo -- tests/doctest_config.md
python -m doctest doctest_config.md
echo -- tests/doctest_test_sum.md
python -m doctest doctest_test_sum.md
echo -- doctest_traceback.md
python -m doctest doctest_traceback.md
echo -- doctest_cache.md
python -m doctest doctest_cache.md

cd ..
