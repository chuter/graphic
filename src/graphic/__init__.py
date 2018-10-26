#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# flake8: noqa

from .meta import __version__
from . import query as gquery
from .shortcuts import node, gquery, use

import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())
