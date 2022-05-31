"""This module is used for testing the perftest CLI program."""
import perftest as pt
import time


def f():
    time.sleep(0.1)


def f2():
    pass


pt.config.set(f, "time", repeat=1, number=1)
pt.config.set(f2, "time", repeat=10, number=10_000)


def perftest_f():
    pt.time_test(f, 0.011, None)


def perftest_f_2():
    pt.time_test(f, 0.011, None)


def perftest_f3():
    pt.time_test(f, 0.11, None)


def perftest_f2():
    pt.time_test(f2, 0.011, None)


def perftest_f2_2():
    pt.time_test(f2, 0.011, None)


def perftest_f2_3():
    pt.time_test(f2, 0.11, None)


# Above where single tests: one test per perftest_ function.
# Below, we combine several tests within one perftest_ function.
# Like in pytest, if only the first test will fail, the other ones
# from this function will not be run.


def perftest_f2_time_and_memory():
    pt.time_test(f2, 0.11, None)
    pt.memory_usage_test(f2, 50, None)

    # these two tests would fail, but only the first one will be run
    pt.memory_usage_test(f2, 2, None)
    pt.memory_usage_test(f2, 1, None)
