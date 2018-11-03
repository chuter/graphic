#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import graphic

from .fixtures import FakeNeo4jDriver


class TestNeo4jFetch:

    def test_empty_nodes_fetch(self, neo4j_graph):
        query = graphic.node().query.limit(0)
        result = neo4j_graph.fetch(query)
        assert result.graph.is_empty()
        assert neo4j_graph._driver is None

    def test_not_empty_nodes_fetch(self, mocker, neo4j_graph):
        query = graphic.node().query.limit(5)

        with mocker.patch.object(FakeNeo4jDriver, 'run', create=True):
            neo4j_graph.fetch(query)
            neo4j_graph._driver.run.assert_called_once_with(
                neo4j_graph.compile(query)
            )
