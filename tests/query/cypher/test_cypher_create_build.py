#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import graphic

from graphic.query.cypher.compiler import build as build_create_cypher


class TestCreateQueryBuild:

    def test_empty_nodes_create(self):
        cypher = build_create_cypher(())
        assert cypher == ''

    def test_only_nodes_create(self):
        nodes = [
            graphic.node('Boss')._as('chuter'),
            graphic.node('Boss', uid=1234)._as('saras'),
            graphic.node('Boss', uid=1234, name="robert")._as('robert')
        ]
        cypher = build_create_cypher(nodes)

        assert cypher.find('CREATE (chuter:Boss)') >= 0
        assert cypher.find('CREATE (saras:Boss {uid:1234})') >= 0
        assert cypher.find(
            'CREATE (robert:Boss {uid:1234,name:"robert"})'
        ) >= 0

    def test_nodes_create_with_duplicate_node(self):
        nodes = [
            graphic.node('Boss')._as('chuter'),
            graphic.node('Boss')._as('chuter')
        ]
        cypher = build_create_cypher(nodes)

        assert cypher == 'CREATE (chuter:Boss)'

    def test_only_relationships_create(self):
        chuter = graphic.node('Boss')._as('chuter')
        saras = graphic.node('Boss')._as('saras')

        relationships = [
            graphic.relationship(chuter, saras, type='TALKTO')._as('cs')
        ]
        cypher = build_create_cypher((), relationships)

        assert cypher.find('CREATE (chuter:Boss)') >= 0
        assert cypher.find('CREATE (saras:Boss)') >= 0
        assert cypher.find('CREATE (chuter)-[cs:TALKTO]->(saras)') >= 0

    def test_nodes_and_relationships_create(self):
        chuter = graphic.node('Boss')._as('chuter')
        saras = graphic.node('Boss')._as('saras')

        relationships = [
            graphic.relationship(chuter, saras, type='TALKTO')._as('cs')
        ]
        cypher = build_create_cypher([chuter, saras], relationships)

        assert cypher.find('CREATE (chuter:Boss)') >= 0
        assert cypher.find('CREATE (saras:Boss)') >= 0
        assert cypher.find('CREATE (chuter)-[cs:TALKTO]->(saras)') >= 0

    def test_relationships_create_with_duplicate(self):
        chuter = graphic.node('Boss')._as('chuter')
        saras = graphic.node('Boss')._as('saras')

        relationships = [
            graphic.relationship(chuter, saras, type='TALKTO')._as('cs'),
            graphic.relationship(chuter, saras, type='TALKTO')._as('cs')
        ]
        cypher = build_create_cypher((), relationships)

        assert cypher.find('CREATE (chuter:Boss)') >= 0
        assert cypher.find('CREATE (saras:Boss)') >= 0

        rel_pos = cypher.find('CREATE (chuter)-[cs:TALKTO]->(saras)')
        assert rel_pos > 0
        assert cypher.find(
            'CREATE (chuter)-[cs:TALKTO]->(saras)',
            rel_pos + 1
        ) == -1
