"""An example config_perftest.py file.

It contains configuration that the perftest CLI command reads before
running the performance tests.
"""
import perftest as pt

pt.log_to_file = True
pt.config.log_file = "perftest.log"
pt.config.digits_for_printing = 5
