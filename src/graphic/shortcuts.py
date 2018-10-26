#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from importlib import import_module

from .graph import RemoteGraph, GraphEntity, Node
from .gquery import GQuery


def node(*labels, **properties):
    """
    Shorcut for build new node

    use node().nameas('${name}') to use the name to identify the node

    In the query context, if you reffer the node which occured in the
    prever statement, then, nameas if useful

    Args:
      labels: node labels
      properties: node (k,v)... properties

    Returns:
      Node instance

    """
    return Node(*labels, **properties)


def gquery(*entities):
    """
    Shortcut for build graph query

    Args:
      entities: one or more graph entities: Node, Edge, Path

    Returns:
      GQuery instance: if entities is empty, the query is to match all nodes
                       of the graph

    """

    if not all(isinstance(e, GraphEntity) for e in entities):
        raise AttributeError('only surpport for GraphEntity type')

    return GQuery(*entities)


def use(engine='graphic.engine.neo4j', **config):
    """
    Shortcut for build graph instance interact with the server which
    the graph db deployed

    Only support eno4j right now

    TODO(chuter): to add more config parameters support for tuning the
    connection with server, like read/write timeout, retry times etc.

    Args:
      engine: default is 'graphic.engine.eno4j'
      config: ie: {
                'URI': 'bolt://localhost',
                'USER': 'neo4j',
                'PASSWORD': 'test'
              }

    """

    import_module(engine)
    return RemoteGraph(engine, **config)
