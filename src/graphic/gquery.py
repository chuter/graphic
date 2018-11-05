#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import copy

from .graph import GraphEntity
from .query.query_utils import Q, Field, Expression


__all__ = ['GQuery']


class Context:

    FIELD_LOOKUP_SPLIT_BYS = ('__', '.', )

    __slots__ = ('_name_2_ent')

    def __init__(self):
        self._name_2_ent = {}

    def __contains__(self, key):
        return key in self._name_2_ent

    def clone(self):
        cloned = type(self)()
        cloned._name_2_ent = copy.copy(self._name_2_ent)
        return cloned

    def add(self, *entities):
        if not all(isinstance(e, GraphEntity) for e in entities):
            raise TypeError('can only accept GraphEntity')

        for entity in entities:
            self._add(entity)

        return self

    def _add(self, entity):
        if entity.is_path():
            raise NotImplementedError('not support path yet')

        self.add_ref(entity.alias, entity)
        if entity.is_edge():
            for node in entity.nodes:
                self.add_ref(node.alias, node)

    def add_ref(self, name, val):
        if name in self._name_2_ent:
            raise KeyError(
                '{} has already to use to ref to {}'.format(
                    name,
                    self._name_2_ent.get(name).__repr__()
                )
            )
        self._name_2_ent[name] = val

    def get(self, name):
        """
        Raises:
          KeyError
        """
        return self._name_2_ent.get(name)

    def lookup_field(self, exp) -> Field:
        """
        Args:
          exp: all support expressions: a__id, a.id, id
        """

        target_ent_alias = GraphEntity.DEFAULT_ALIAS
        field_name = exp

        for split_by in self.FIELD_LOOKUP_SPLIT_BYS:
            if split_by in exp:
                try:
                    target_ent_alias, field_name = exp.split(split_by)
                except:  # noqa
                    raise ValueError(exp)
                else:
                    break

        target_ent = self.get(target_ent_alias)
        return Field(target_ent, field_name)


class GQuery:
    # TODO(chuter): support path
    _LIMIT = 20

    __slots__ = ('_where', '_entities', '_context',
                 '_select', '_limit', '_order_by')

    def __init__(self, *entities):
        self._where = Q()
        self._entities = entities[:]
        self._context = Context().add(*entities)
        self._select = set()
        self._limit = self._LIMIT
        self._order_by = None

        for entity in entities:
            self._add_filter_by_entity_properties(entity)

    def _add_filter_by_entity_properties(self, entity):
        for name, val in entity:
            if entity.alias != entity.DEFAULT_ALIAS:
                left_exp = Expression.LOOKUP_SPLIT_BY.join([
                    entity.alias,
                    name
                ])
            else:
                left_exp = name
            kwargs = dict(((left_exp, val),))
            self.filter(**kwargs)

        if entity.is_edge():
            for node in entity.nodes:
                self._add_filter_by_entity_properties(node)

    @property
    def context(self):
        return self._context.clone()

    @property
    def queryfor(self):
        return self._entities

    @property
    def where(self):
        return self._where._clone()

    @property
    def returns(self):
        return frozenset(self._select)

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

    def select(self, *exps):
        for exp_item in exps:
            if isinstance(exp_item, str):
                exp_item = self.context.lookup_field(exp_item)

            self._select.add(exp_item)

        return self

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
