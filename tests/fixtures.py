#!/usr/bin/env python
# -*- encoding: utf-8 -*-


class FakeNeo4jDriver(object):

    def __init__(self, uri, **config):
        super().__init__()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def session(self, *args, **config):
        return self
