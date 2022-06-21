"""This module is used for testing the perftest CLI program."""
import perftest as pt
import time


def f2():
    time.sleep(0.05)


pt.config.set(f2, "time", number=1, repeat=2)


def perftest_f():
    pt.time_test(f2, raw_limit=0.051)
