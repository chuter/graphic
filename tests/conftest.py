#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pytest
from neo4j import GraphDatabase

import graphic
from .fixtures import FakeNeo4jDriver


def new_fake_driver(uri, **config):
    return FakeNeo4jDriver(uri)


GraphDatabase.driver = new_fake_driver


@pytest.fixture
def neo4j_graph():
    return graphic.use_neo4j()
