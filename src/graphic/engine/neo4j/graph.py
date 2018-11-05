#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import copy

from neo4j import GraphDatabase, basic_auth

from graphic.engine import Result
from graphic.graph import RemoteGraph
from graphic.query.cypher.compiler import compile as compile_as_cypher
from graphic.query.cypher.compiler import build as build_create_cypher


__all__ = ['Neo4jGraph']


_DEFAULT_CONFIG = {
    "URI": "bolt://localhost",
    "USER": "neo4j",
    "PASSWORD": "test"
}


# TODO(chuter):
#   1. excpetions process
#   2. hydrate to graphic Result, Graph

class Neo4jGraph(RemoteGraph):
    """Not thread safe!!!"""

    __slots__ = ('_driver', '_config')

    engine = 'graphic.engine.neo4j'

    def __init__(self, *args, **config):
        self._config = copy.copy(_DEFAULT_CONFIG)
        self._config.update(config)

        self._driver = None

    def compile(self, gquery):
        return compile_as_cypher(gquery)

    def fetch(self, gquery):
        if gquery is None or gquery.limit() == 0:
            return Result(DummyEmptyGraphProxy())

        cypher_query = self.compile(gquery)
        return Result(self._run(cypher_query))

    def push(self, *graph_entities):
        """
        Add nodes, relationships to the neo4j server instance

        It first deal with all the nodes, then all the relationships,
        """
        # TODO(chuter):
        #   0. add path surpport
        #   1. auto covert create to merge to avoid duplicate!!!
        #   2. auto build alias for each entity whichout one
        _nodes = []
        _relationships = []

        for ent in graph_entities:
            if ent.is_node():
                _nodes.append(ent)
            if ent.is_edge():
                _relationships.append(ent)

        if len(_nodes) == 0:
            return Result(DummyEmptyGraphProxy())

        cypher_query = build_create_cypher(_nodes, _relationships)
        return Result(self._run(cypher_query))

    @property
    def config(self):
        return copy.copy(self._config)

    def _run(self, cypher_query):
        if self._driver is None:
            config = self.config
            self._driver = GraphDatabase.driver(
                config['URI'],
                auth=basic_auth(config["USER"], config["PASSWORD"])
            )

        with self._driver.session() as session:
            return session.run(cypher_query)


class DummyEmptyGraphProxy:

    def graph(self):
        return self

    def records(self):
        return tuple()

    @property
    def nodes(self):
        return tuple()

    @property
    def relationships(self):
        return tuple()
