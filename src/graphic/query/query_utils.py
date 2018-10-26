#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import copy


class Q(object):
    AND = 'AND'
    OR = 'OR'

    __slots__ = ('_children', '_connector', '_negated')

    def __init__(self, *args, **kwargs):
        self._children = list(args) + sorted(kwargs.items())
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
        template = '(NOT (%s: %s))' if self.negated else '(%s: %s)'
        return template % (
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
