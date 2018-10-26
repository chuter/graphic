#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from graphic.graph import RemoteGraph
from graphic.query.cypher.compiler import compile as compile_as_cypher

from .funcs import lookup_func as lookup_neo4j_funcs

__all__ = ['Graph']


_DEFAULT_CONFIG = {
    "URL": "bolt://localhost",
    "USER": "neo4j",
    "PASSWORD": "test"
}


class Graph(RemoteGraph):

    engine = 'graphic.engine.neo4j'

    def __init__(self, *args, **config):
        # TODO(chuter) build neo4j driver instance due to config
        pass

    def compile(self, gquery):
        return compile_as_cypher(lookup_neo4j_funcs, gquery)
