"""An example config_perftester.py file.

It contains configuration that the perftester CLI command reads before
running the performance tests.
"""
import perftester as pt

pt.log_to_file = True
pt.config.log_file = "perftester.log"
pt.config.digits_for_printing = 5
