#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from six import with_metaclass

from collections import Mapping, Hashable

from .utils import check_methods


class Graph(object):
    pass


class RemoteGraphMeta(type):
    __slots__ = ()
    _engine_2_class = {}

    def __new__(cls, name, bases, attrs, **kwargs):
        cls = super().__new__(cls, name, bases, attrs, **kwargs)

        engine = attrs.get('engine', None)
        if engine is not None:
            cls._engine_2_class[engine] = cls

        return cls

    @classmethod
    def get_engine_class(cls, engine):
        return cls._engine_2_class.get(engine, None)


class RemoteGraph(with_metaclass(RemoteGraphMeta)):

    __slots__ = ()

    def __new__(cls, engine, *args, **config):
        target_cls = cls.get_engine_class(engine)
        if target_cls is None:
            raise AttributeError(
                'Not surpport engine for {},'
                'please make sure the target engine can be import'.format(
                    engine
                )
            )

        return object.__new__(target_cls, *args, **config)

    def compile(self, gquery, context):
        """
        compile query for the target query string which used to send
        to the db server to do request

        Args:
          gquery: GQuery instance

        Returns:
          query string to send to db server

        """
        raise NotImplementedError

    def fetch(self, gquery):
        pass

    def push(self, graph_or_gquery, proc_func_for_fetch=None):
        pass

    def delete(self, gquery):
        pass


class GraphEntity(Mapping, Hashable):
    __slots__ = ('_kv_paires', '_id', '_alias')

    def __init__(self, id=None, **properties):
        self._kv_paires = properties
        self._id = id
        self._alias = '_'

    def __getitem__(self, key):
        return self._kv_paires[key]

    def __len__(self):
        return len(self._kv_paires)

    def __iter__(self):
        return self._kv_paires.items().__iter__()

    def __getattr__(self, key):
        return self.get(key)

    def __hash__(self):
        return self.id or self.alies

    @classmethod
    def __subclasshook__(cls, C):
        if cls is GraphEntity:
            if not all(issubclass(C, c) for c in {Mapping, Hashable}):
                return False

            return check_methods(
                C,
                "id", "walk", "is_node", "is_path", "is_edge"
            )
        return NotImplemented

    @property
    def id(self):
        return self._id

    @property
    def alias(self):
        return self._alias

    def _as(self, alias):
        """
        Alias for the entity.
        Very useful when build query in complex context. Can ref to any
        entity in later clauses in the query context
        """
        self._alias = alias
        return self

    def walk(self, cb):
        raise NotImplementedError

    def is_node(self):
        return False

    def is_path(self):
        return False

    def is_edge(self):
        return False


class Node(GraphEntity):

    __slots__ = GraphEntity.__slots__ + ('_labels', )

    def __init__(self, *labels, id=None, **properties):
        super(Node, self).__init__(id=id, **properties)
        self._labels = frozenset(labels)

    @property
    def labels(self):
        return self._labels

    def __hash__(self):
        return '{}<{}>'.format(':'.join(self.labels), self.id)

    def is_node(self):
        return True

    def walk(self, cb):
        cb(self)
