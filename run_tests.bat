:: Run all doctests
echo Grab a cup of coffee as this will take some time, my friend...

python -m doctest README.md 

cd ./perftester
python -m doctest perftester.py

cd ../docs
python -m doctest benchmarking_against_another_function.md
python -m doctest most_basic_use_time.md
python -m doctest use_of_config.md
python -m doctest most_basic_use_memory.md
python -m doctest README.md
python -m doctest use_case_raw_time_testing.md
python -m doctest change_benchmarking_function.md

cd ../tests
python -m doctest doctest_function_str.md
python -m doctest doctest_function_floats.md
python -m doctest doctest_config.md
python -m doctest doctest_test_sum.md
python -m doctest doctest_traceback.md
python -m doctest doctest_cache.md

cd ..
