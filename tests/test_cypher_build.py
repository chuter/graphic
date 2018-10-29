#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pytest

import graphic
from graphic import gquery


class TestSingleEntitySingleMatchQueryBuild:

    @pytest.mark.parametrize("node, expected_cyphe", [
        (
            graphic.node(),
            (
                r'MATCH (_) RETURN id(_) LIMIT 20'
            )
        ),
        (
            graphic.node()._as('geek'),
            (
                r'MATCH (geek) RETURN id(geek) LIMIT 20'
            )
        ),
        (
            graphic.node(uid=12345),
            r'MATCH (_) WHERE _.uid=12345 RETURN id(_) LIMIT 20'
        ),
        (
            graphic.node("User", uid=12345),
            r'MATCH (_:User) WHERE _.uid=12345 RETURN id(_) LIMIT 20'
        ),
        (
            graphic.node("User", uid=12345)._as('geek'),
            r'MATCH (geek:User) WHERE geek.uid=12345 RETURN id(geek) LIMIT 20'
        ),
        (
            graphic.node("User", uid=12345, name="chuter")._as('geek'),
            ((
                r'MATCH (geek:User) WHERE (geek.uid=12345 AND '
                r'geek.name="chuter") RETURN id(geek) LIMIT 20'
            ), (
                r'MATCH (geek:User) WHERE (geek.name="chuter" AND '
                r'geek.uid=12345") RETURN id(geek) LIMIT 20'
            ), )
        )
    ])
    def test_build_only_dueto_node(self, node, expected_cyphe):
        q = gquery(node)
        remote_graph = graphic.use()

        if isinstance(expected_cyphe, (tuple, list)):
            assert remote_graph.compile(q) in expected_cyphe
        else:
            assert expected_cyphe in remote_graph.compile(q)

    def test_generate_name_for_entity(self):
        # TODO implemant
        pass

    def test_cyphe_escape(self):
        # TODO(chuter) escape ", etc. for cyphe
        # TODO implemant
        pass
