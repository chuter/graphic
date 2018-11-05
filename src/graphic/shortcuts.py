#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import warnings
from importlib import import_module

from .graph import RemoteGraph, Node, Relationship
from .compat import ModuleNotFoundError


def node(*labels, **properties) -> Node:
    """
    Shorcut for build new node

    use node()._as('${alias}') to use the alias to identify the node

    In the query context, if you reffer the node which occured in the
    prever statement, then, alias if useful

    Args:
      labels: node labels
      properties: node (k,v)... properties

    Returns:
      Node instance

    """
    return Node(*labels, **properties)


def relationship(node_from, node_to, type=None,
                 with_direction=True, **properties) -> Relationship:
    """
    Shorcut for build new relationship

    use relationship()._as('${alias}') to use the alias to identify the
    relationship

    In the query context, if you reffer the relationship which occured in the
    prever statement, then, alias if useful

    Args:
      node_from: from node
      node_to: to node
      type: relationship type
      with_direction: whether is node_from direct to node_to
      properties: relationship k,v pairs properties

    """
    return Relationship(
        node_from,
        node_to,
        type=type,
        with_direction=with_direction,
        **properties
    )


def link(node_from, node_to, type=None, **properties) -> Relationship:
    """Create new relationship without derection of two nodes
    """
    return relationship(
        node_from,
        node_to,
        type=type,
        with_direction=False,
        **properties
    )


def use(engine='graphic.engine.neo4j', **config) -> RemoteGraph:
    """
    Shortcut for build graph instance interact with the server which
    the graph db deployed

    Only support neo4j right now

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

    try:
        import_module(engine)
    except ModuleNotFoundError:
        warnings.warn(
            'can not import engine({}) module'.format(engine),
            ImportWarning
        )

    return RemoteGraph(engine, **config)


def use_neo4j(**config):
    """See also use"""

    return use(**config)
