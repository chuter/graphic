#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from itertools import chain
from six import with_metaclass

from collections import Mapping, Hashable

from .utils import check_methods


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
    # TODO(chuter) define the unified exceptions

    __slots__ = ()

    def __new__(cls, engine, *args, **config):
        target_cls = cls.get_engine_class(engine)
        if target_cls is None:
            raise AttributeError(
                'Not surpport engine for {}, '
                'please make sure the target engine can be import'.format(
                    engine
                )
            )

        ins = object.__new__(target_cls)
        ins.__init__(*args, **config)
        return ins

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
        """
        fetch graph data from graph db server

        Args:
          gquery: GQuery instance

        Returns:
          graphic.engine.Result instance

        """
        raise NotImplementedError

    def push(self, *graph_entities):
        """
        Add new nodes, relationships to the graph

        Args:
          graph_entities: nodes, relationships or pathes

        """
        # TODO(chuter):
        #   1. receive Graph object as parameter, return Graph object
        #   2. support create or update
        #   3. support create from query(unwind)
        raise NotImplementedError


# TODO(chuter): auto generate default alias?
class GraphEntity(Mapping, Hashable):

    DEFAULT_ALIAS = '_'

    __slots__ = ('_kv_paires', '_alias')

    def __init__(self, **properties):
        self._kv_paires = properties
        self._alias = self.DEFAULT_ALIAS

    def __getitem__(self, key):
        return self._kv_paires[key]

    def __len__(self):
        return len(self._kv_paires)

    def __iter__(self):
        return iter(self._kv_paires.items())

    def __getattr__(self, key):
        return self.get(key)

    @classmethod
    def __subclasshook__(cls, C):
        if cls is GraphEntity:
            return check_methods(
                C,
                "is_node", "is_path", "is_edge"
            )
        return NotImplemented

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

    def is_node(self):
        return False

    def is_path(self):
        return False

    def is_edge(self):
        return False

    @property
    def query(self):
        from .gquery import GQuery
        return GQuery(self)


class Node(GraphEntity):

    __slots__ = GraphEntity.__slots__ + ('_id', '_labels')

    def __init__(self, *labels, id=None, **properties):
        super().__init__(**properties)
        self._id = id
        self._labels = frozenset(labels)

    def __eq__(self, that):
        if self is that:
            return True

        if self.id is not None and that.id is not None:
            return self.id == that.id

        return hash(self) == hash(that)

    @property
    def labels(self):
        return self._labels

    @property
    def id(self):
        return self._id

    def __str__(self):
        if self.id is not None:
            return '<{}>'.format(self.id)

        return '({}:{})'.format(self.alias, ':'.join(self.labels))

    def __hash__(self):
        if self.id is not None:
            return int(self.id)

        return hash(self.__str__())

    def is_node(self):
        return True


class Relationship(GraphEntity):

    __slots__ = GraphEntity.__slots__ + (
        '_node_from', '_node_to', '_type', '_with_direction'
    )

    def __init__(self, node_from, node_to, type=None,
                 with_direction=True, **properties):
        super().__init__(**properties)
        self._node_from = node_from
        self._node_to = node_to
        self._with_direction = with_direction
        self._type = type

    @property
    def node_from(self):
        return self._node_from

    @property
    def node_to(self):
        return self._node_to

    @property
    def type(self):
        return self._type

    @property
    def nodes(self):
        yield self.node_from
        yield self.node_to

    @property
    def with_direction(self):
        return self._with_direction

    def __str__(self):
        str_parts = [self.node_from.__str__(), '-']

        if self.type is not None:
            str_parts.extend(['[', '{}:{}'.format(self.alias, self.type), ']'])
        else:
            str_parts.append('[{}]'.format(self.alias))

        str_parts.append('-')

        if self.with_direction:
            str_parts.append('>')

        str_parts.append(self.node_to.__str__())

        return ''.join(str_parts)

    def __hash__(self):
        if self.type is None:
            return hash(self.node_from) ^ hash(self.node_to)

        return hash(self.node_from) ^ hash(self.type) ^ hash(self.node_to)

    def is_edge(self):
        return True


class Path(GraphEntity):
    __slots__ = GraphEntity.__slots__ + (
        '_start_node', '_end_node', '_min_len', '_max_len'
    )

    def __init__(self, node_from, node_to, type=None,
                 with_direction=True, **properties):
        super().__init__(**properties)
        self._node_from = node_from
        self._node_to = node_to
        self._with_direction = with_direction
        self._type = type

    @property
    def node_from(self):
        return self._node_from

    @property
    def node_to(self):
        return self._node_to

    @property
    def type(self):
        return self._type

    @property
    def nodes(self):
        yield self.node_from
        yield self.node_to

    @property
    def with_direction(self):
        return self._with_direction

    def __str__(self):
        str_parts = [self.node_from.__str__(), '-']

        if self.type is not None:
            str_parts.extend(['[', '{}:{}'.format(self.alias, self.type), ']'])
        else:
            str_parts.append('[{}]'.format(self.alias))

        str_parts.append('-')

        if self.with_direction:
            str_parts.append('>')

        str_parts.append(self.node_to.__str__())

        return ''.join(str_parts)

    def __hash__(self):
        if self.type is None:
            return hash(self.node_from) ^ hash(self.node_to)

        return hash(self.node_from) ^ hash(self.type) ^ hash(self.node_to)

    def is_path(self):
        return True


class SubGraph:
    # TODO(chuter) add any nodes, relationships and pathes!!!
    """Arbitrary, unordered collection of nodes and relationships."""

    __slots__ = ('_nodes', '_relationships', )

    def __init__(self, nodes=None, relationships=None):
        self._nodes = frozenset(nodes or [])
        self._relationships = frozenset(relationships or [])
        self._nodes |= frozenset(
            chain(*(r.nodes for r in self._relationships))
        )

    def __eq__(self, other):
        # TODO(chuter) if only summary, check summary??
        try:
            return all([
                self.nodes == other.nodes,
                self.relationships == other.relationships
            ])
        except (AttributeError, TypeError):
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        value = 0
        for _ in self._nodes:
            value ^= hash(_)
        for _ in self._relationships:
            value ^= hash(_)
        return value

    def __iter__(self):
        return chain(iter(self._nodes), iter(self._relationships))

    def __or__(self, other):
        return type(self)(
            nodes=self.nodes | other.nodes,
            relationships=self.relationships | other.relationships
        )

    def __and__(self, other):
        return type(self)(
            nodes=self.nodes & other.nodes,
            relationships=self.relationships & other.relationships
        )

    def __sub__(self, other):
        r = self.relationships - other.relationships
        n = self.nodes - other.nodes | set().union(*(_.nodes for _ in r))
        return type(self)(nodes=n, relationships=r)

    def __xor__(self, other):
        r = self.relationships ^ other.relationships
        n = (self.nodes ^ other.nodes) | set().union(*(_.nodes for _ in r))
        return type(self)(nodes=n, relationships=r)

    @property
    def nodes(self):
        return self._nodes

    @property
    def relationships(self):
        return self._relationships

    def is_empty(self):
        return len(self.nodes) == 0


Graph = SubGraph
