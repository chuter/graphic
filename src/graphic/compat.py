#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import sys

_ver = sys.version_info


def is_py37():
    return _ver.major == 3 and _ver.minor == 7


try:
    import ModuleNotFoundError
except ImportError:
    ModuleNotFoundError = ImportError
