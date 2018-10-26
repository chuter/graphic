#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import copy

from .graph import GraphEntity
from .query.query_utils import Q


__all__ = ['GQuery']


class Context(object):

    __slots__ = ('_dict')

    def __init__(self):
        self._dict = {}

    def __contains__(self, key):
        return key in self._dict

    def clone(self):
        cloned = type(self)()
        cloned._dict = copy.copy(self._dict)
        return cloned

    def add(self, *entities):
        if not all(isinstance(e, GraphEntity) for e in entities):
            raise TypeError('can only accept GraphEntity')

        for entity in entities:
            entity.walk(lambda node_or_edge: (
                self.add_ref(node_or_edge.alias, node_or_edge)
                if node_or_edge.alias
                else
                None
            ))
        return self

    def add_ref(self, name, val):
        if name in self._dict:
            raise KeyError(
                '{} has already to use to ref to {}'.format(
                    name,
                    self._dict.get(name).__repr__()
                )
            )
        self._dict[name] = val

    def get(self, name):
        """
        Raises:
          KeyError
        """
        return self._dict.get(name)


class GQuery(object):

    __slots__ = ('_where', '_entities', '_context', '_limit', '_order_by')

    def __init__(self, *entities):
        self._where = Q()
        self._entities = entities[:]
        self._context = Context().add(*entities)

        for entity in entities:
            for name, val in entity:
                if entity.alias != '_':
                    left_epr = '{}__{}__eq'.format(entity.alias, name)
                else:
                    left_epr = '{}__eq'.format(name)
                kwargs = dict(((left_epr, val),))
                self.filter(**kwargs)

        self._limit = 20
        self._order_by = None

    @property
    def context(self):
        return self._context.clone()

    @property
    def queryfor(self):
        return self._entities

    @property
    def where(self):
        return self._where

    def filter(self, *qargs, **kwargs):
        """
        examples:

        query.filter(name__eq="chuter", age__gte=32)
        query.filter(Q(name__eq="chuter") & Q(age__gte=32))

        the top two are equal

        q = Q(name__eq="chuter", age__gte=32)
        q |= Q(comp__eq="BOSS")
        query.filter(q)
        """
        self._where &= Q(*qargs, **kwargs)
        return self

    def select(self):
        # select files to return, aggregations support
        pass

    def order_by(self, by=None):
        if by is None:
            return self._order_by

        self._order_by = by
        return self

    def limit(self, to=None):
        if to is None:
            return self._limit

        self._limit = to
        return self
