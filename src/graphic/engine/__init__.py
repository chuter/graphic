#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# TODO(chuter):
#   1. Unify the defination of Graph, Node, Relationship and Path used
#      both in query description and fetch result.
#   2. Implement hydrator for neo4j bolt


from graphic import Graph


__all__ = ['Result']


class Result:
    """
    Unify the interface for interact with the specific driver result.

    Current only for neo4j, It proxy to the neo4j-driver native object
    for the actual data.

    """

    __slots__ = ('_proxyto', )

    def __init__(self, proxyto):
        self._proxyto = proxyto

    @property
    def graph(self):
        _native_graph = self._proxyto.graph()

        return Graph(
            nodes=iter(_native_graph.nodes),
            relationships=iter(_native_graph.relationships)
        )

    @property
    def records(self):
        return self._proxyto.records()
