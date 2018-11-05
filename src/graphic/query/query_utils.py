#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import copy

from .func import Func
from .func import lookup_func
from .func import eq


class Expression:
    r"""
    Used in query filter clause:

    only support follow formats:
        id=12
        a__id=12
        id__gte=12
        a__age__gt=30

    """

    __slots__ = ('_context')

    LOOKUP_SPLIT_BY = '__'

    @classmethod
    def parse(cls, exp_str, val) -> Func:
        parts = exp_str.split(cls.LOOKUP_SPLIT_BY)

        _size = len(parts)
        if _size == 1:  # id=2
            return eq(exp_str, val)
        elif _size == 2:
            target_func = lookup_func(parts[-1])
            if target_func is None:  # a__id=12
                return eq(exp_str, val)
            else:  # id__gte=12
                return target_func(cls.LOOKUP_SPLIT_BY.join(parts[0:-1]), val)
        elif _size == 3:  # a__age__gt=30
            target_func = lookup_func(parts[-1])
            if target_func is None:
                raise ValueError('Not support func {} yet'.format(parts[-1]))

            return target_func(cls.LOOKUP_SPLIT_BY.join(parts[0:-1]), val)


class Field:

    __slots__ = ('_ent', '_field_name')

    PK = 'id'

    def __init__(self, graph_entity, field_name):
        self._ent = graph_entity
        self._field_name = field_name

    def __call__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        if self._field_name == self.PK:
            return '{}({})'.format(self.PK, self._ent.alias)

        return '{}.{}'.format(
            self._ent.alias,
            self._field_name
        )


class Q:
    AND = 'AND'
    OR = 'OR'

    __slots__ = ('_children', '_connector', '_negated')

    def __init__(self, *args, **kwargs):
        self._children = list(args)

        for exp_str, val in kwargs.items():
            self._children.append(Expression.parse(exp_str, val))

        self._connector = self.AND
        self._negated = False

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj._add(self, self.AND)
        obj.negate()
        return obj

    def __str__(self):
        tmpl = '(NOT (%s: %s))' if self.negated else '(%s: %s)'
        return tmpl % (
            self.connector,
            ', '.join(str(c) for c in self.children)
        )

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)

    def __len__(self):
        """Return the number of children this node has."""
        return len(self.children)

    def __contains__(self, other):
        """Return True if 'other' is a direct child of this instance."""
        return other in self.children

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return (
            self.connector,
            self.negated
        ) == (
            other.connector,
            other.negated
        ) and self.children == other.children

    def __deepcopy__(self, memodict):
        cpy_q = type(self)()
        cpy_q._connector = self._connector
        cpy_q._negated = self.negated
        cpy_q._children = copy.deepcopy(self.children, memodict)
        return cpy_q

    def _combine(self, other, conn):
        if not isinstance(other, type(self)):
            raise TypeError(other)

        # If the other Q() is empty, ignore it and just use `self`.
        if len(other) == 0:
            return copy.deepcopy(self)
        # Or if this Q is empty, ignore it and just use `other`.
        elif len(self) == 0:
            return copy.deepcopy(other)

        obj = type(self)()
        obj._connector = conn
        obj._add(self, conn)
        obj._add(other, conn)
        return obj

    def _clone(self):
        cloned = type(self)()
        cloned._connector = self._connector
        cloned._negated = self.negated
        cloned._children = self.children
        return cloned

    @property
    def connector(self):
        return self._connector

    @property
    def children(self):
        return self._children

    @property
    def negated(self):
        return self._negated

    def negate(self):
        """Negate the sense of the root connector."""
        self._negated = not self.negated

    def _add(self, other, conn_type):
        if other in self.children:
            return self

        if self.connector == conn_type:
            if all((
                not other.negated,
                (other.connector == conn_type or len(other) == 1)
            )):
                self.children.extend(other.children)
            else:
                self.children.append(other)
        else:
            sub_q = self._clone()
            self._connector = conn_type
            self._children = [sub_q, other]

        return self
