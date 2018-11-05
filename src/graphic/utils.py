#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import sys


_ver = sys.version_info


def is_py37():
    return _ver.major == 3 and _ver.minor == 7


def check_methods(C, *methods):
    mro = C.__mro__
    for method in methods:
        for B in mro:
            if method in B.__dict__:
                if B.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented
    return True
