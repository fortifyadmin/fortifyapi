import sys
import pytest


def f(name):
    print("Hello {}".format(name))


def test_f(capfd):
    f("FortifyApi")

    out, err = capfd.readouterr()
    assert out == "Hello FortifyApi\n"
