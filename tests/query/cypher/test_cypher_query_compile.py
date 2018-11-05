#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pytest

import graphic
from graphic.query.func import avg
from graphic.query.cypher.compiler import compile as compile_cypher


class TestSingleNodeSingleMatchQueryCompile:

    @pytest.mark.parametrize("node, expected_cyphe", [
        (
            graphic.node(),
            (
                r'MATCH (_) RETURN _ LIMIT 20'
            )
        ),
        (
            graphic.node()._as('geek'),
            (
                r'MATCH (geek) RETURN geek LIMIT 20'
            )
        ),
        (
            graphic.node(uid=12345),
            r'MATCH (_) WHERE _.uid=12345 RETURN _ LIMIT 20'
        ),
        (
            graphic.node("User", uid=12345),
            r'MATCH (_:User) WHERE _.uid=12345 RETURN _ LIMIT 20'
        ),
        (
            graphic.node("User", uid=12345)._as('geek'),
            r'MATCH (geek:User) WHERE geek.uid=12345 RETURN geek LIMIT 20'
        ),
        (
            graphic.node("User", uid=12345, name="chuter")._as('geek'),
            ((
                r'MATCH (geek:User) WHERE (geek.uid=12345 AND '
                r"geek.name='chuter') RETURN geek LIMIT 20"
            ), (
                r"MATCH (geek:User) WHERE (geek.name='chuter' AND "
                r'geek.uid=12345") RETURN geek LIMIT 20'
            ), )
        )
    ])
    def test_base_query(self, node, expected_cyphe):
        if isinstance(expected_cyphe, (tuple, list)):
            assert compile_cypher(node.query) in expected_cyphe
        else:
            assert expected_cyphe in compile_cypher(node.query)

    @pytest.mark.parametrize("query, expected_cyphe", [
        (
            graphic.node().query.select('id', avg('age')),
            (
                r'MATCH (_) RETURN id(_),avg(_.age) LIMIT 20',
                r'MATCH (_) RETURN avg(_.age),id(_) LIMIT 20',
            )
        ),
        (
            graphic.node()._as('a').query.select('a__id', avg('a__age')),
            (
                r'MATCH (a) RETURN id(a),avg(a.age) LIMIT 20',
                r'MATCH (a) RETURN avg(a.age),id(a) LIMIT 20',
            )
        ),
    ])
    def test_query_with_select(self, query, expected_cyphe):
        if isinstance(expected_cyphe, tuple):
            assert compile_cypher(query) in expected_cyphe
        else:
            assert compile_cypher(query) == expected_cyphe

    @pytest.mark.parametrize("query, expected_cyphe", [
        (
            graphic.node().query.order_by('id'),
            r'MATCH (_) RETURN _ ORDER BY id(_) ASC LIMIT 20',
        ),
        (
            graphic.node().query.order_by('age'),
            r'MATCH (_) RETURN _ ORDER BY _.age ASC LIMIT 20',
        ),
        (
            graphic.node().query.order_by('-id'),
            r'MATCH (_) RETURN _ ORDER BY id(_) DESC LIMIT 20',
        ),
        (
            graphic.node().query.order_by('-age'),
            r'MATCH (_) RETURN _ ORDER BY _.age DESC LIMIT 20',
        ),
        (
            graphic.node()._as('a').query.order_by('a__id'),
            r'MATCH (a) RETURN a ORDER BY id(a) ASC LIMIT 20',
        ),
        (
            graphic.node()._as('a').query.order_by('-a__id'),
            r'MATCH (a) RETURN a ORDER BY id(a) DESC LIMIT 20',
        ),
    ])
    def test_query_with_order_by(self, query, expected_cyphe):
        if isinstance(expected_cyphe, tuple):
            assert compile_cypher(query) in expected_cyphe
        else:
            assert compile_cypher(query) == expected_cyphe


class TestSingleRelationSingleMatchQueryCompile:

    @pytest.mark.parametrize("relationshiop, expected_cyphe", [
        (
            graphic.relationship(
                graphic.node()._as('b'),
                graphic.node()._as('g')
            ),
            r'MATCH (b)-[_]->(g) RETURN _ LIMIT 20'
        ),
        (
            graphic.link(
                graphic.node()._as('b'),
                graphic.node()._as('g'),
            ),
            r'MATCH (b)-[_]-(g) RETURN _ LIMIT 20'
        ),
        (
            graphic.relationship(
                graphic.node()._as('b'),
                graphic.node()._as('g'),
            )._as('r'),
            r'MATCH (b)-[r]->(g) RETURN r LIMIT 20'
        ),
        (
            graphic.relationship(
                graphic.node()._as('b'),
                graphic.node()._as('g'),
                type='TALKTO'
            )._as('r'),
            r'MATCH (b)-[r:TALKTO]->(g) RETURN r LIMIT 20'
        ),
        (
            graphic.relationship(
                graphic.node('Boss')._as('b'),
                graphic.node('Geek')._as('g'),
            ),
            r'MATCH (b:Boss)-[_]->(g:Geek) RETURN _ LIMIT 20'
        ),
        (
            graphic.relationship(
                graphic.node('Boss', uid=1234)._as('b'),
                graphic.node('Geek')._as('g'),
            ),
            r'MATCH (b:Boss)-[_]->(g:Geek) WHERE b.uid=1234 RETURN _ LIMIT 20'
        ),
        (
            graphic.relationship(
                graphic.node('Boss', uid=1234)._as('b'),
                graphic.node('Geek', uid=2345)._as('g'),
            ),
            (
                r'MATCH (b:Boss)-[_]->(g:Geek) WHERE (b.uid=1234 AND '
                r'g.uid=2345) RETURN _ LIMIT 20'
            )
        )
    ])
    def test_build_only_dueto_relationship(self, relationshiop,
                                           expected_cyphe):
        assert expected_cyphe == compile_cypher(relationshiop.query)
