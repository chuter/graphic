#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import graphic

from graphic.query.cypher.compiler import build as build_create_cypher
from .fixtures import FakeNeo4jDriver


class TestNeo4jPush:

    def test_empty_nodes_push(self, neo4j_graph):
        result = neo4j_graph.push()
        assert result.graph.is_empty()
        assert neo4j_graph._driver is None

    def test_only_nodes_push(self, mocker, neo4j_graph):
        nodes = [
            graphic.node('Boss')._as('chuter'),
            graphic.node('Boss', uid=1234)._as('saras'),
            graphic.node('Boss', uid=1234, name="robert")._as('robert')
        ]
        with mocker.patch.object(FakeNeo4jDriver, 'run', create=True):
            neo4j_graph.push(*nodes)
            neo4j_graph._driver.run.assert_called_once_with(
                build_create_cypher(nodes)
            )

    def test_nodes_and_relationships_push(self, mocker, neo4j_graph):
        chuter = graphic.node('Boss')._as('chuter')
        saras = graphic.node('Boss')._as('saras')
        robert = graphic.node('Geak')._as('robert')

        relation_ships = [
            graphic.relationship(chuter, saras, type='TALKTO')._as('cs'),
            graphic.relationship(
                chuter,
                robert,
                type='TALKTO',
                timestamp=1234660
            )._as('cr')
        ]

        with mocker.patch.object(FakeNeo4jDriver, 'run', create=True):
            neo4j_graph.push(chuter, *relation_ships)
            neo4j_graph._driver.run.assert_called_once_with(
                build_create_cypher([chuter, saras, robert], relation_ships)
            )
