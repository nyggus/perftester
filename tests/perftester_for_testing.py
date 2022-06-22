"""This module is used for testing the perftester CLI program."""
import perftester as pt
import time


def f():
    time.sleep(0.1)


def f2():
    pass


pt.config.set(f, "time", repeat=1, number=1)
pt.config.set(f2, "time", repeat=10, number=10_000)


def perftester_f():
    pt.time_test(f, raw_limit=0.011)


def perftester_f_2():
    pt.time_test(f, raw_limit=0.011)


def perftester_f3():
    pt.time_test(f, raw_limit=0.11)


def perftester_f2():
    pt.time_test(f2, raw_limit=0.011)


def perftester_f2_2():
    pt.time_test(f2, raw_limit=0.011, Number=10000, Repeat=7)


def perftester_f2_3():
    pt.time_test(f2, raw_limit=0.11)


# Above where single tests: one test per perftester_ function.
# Below, we combine several tests within one perftester_ function.
# Like in pytest, if only the first test will fail, the other ones
# from this function will not be run.


def perftester_f2_time_and_memory():
    pt.time_test(f2, raw_limit=0.11)
    pt.memory_usage_test(f2, raw_limit=50)

    # these two tests would fail, but only the first one will be run
    pt.memory_usage_test(f2, raw_limit=2)
    pt.memory_usage_test(f2, raw_limit=1)
