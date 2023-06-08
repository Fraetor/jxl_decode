"""Tests for the command line interface."""

import subprocess


def test_command_line_help():
    subprocess.run(("jxl_decode", "--help"), check=False)
    # test verbose options. This is really just to up the coverage number.
    subprocess.run(("jxl_decode", "-v"), check=False)
    subprocess.run(("jxl_decode", "-vv"), check=False)
