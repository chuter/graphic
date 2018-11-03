#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from typing import Iterable

from graphic.query.func import Func, Aggregation


__all__ = ['compile', 'build']


# TODO(chuter):
#   1. compile to string and parameters
#   2. cypher escape
#   3. auto convert create to merge

def compile_where_clause(gquery):

    def compile_q(q):
        if isinstance(q, Func):
            return q(lookup_field=gquery.context.lookup_field)

        if len(q) == 0:
            return ''

        if len(q) > 1:
            join_by = ' {} '.format(q.connector)
            return (
                '({})'.format(
                    join_by.join([compile_q(child) for child in q.children])
                )
            )

        return compile_q(q.children[0])

    return compile_q(gquery.where)


def compile_match_clause(*entities):
    def hydrage_entity(entity):
        if entity.is_node():
            node_labels = entity.labels
            if len(node_labels) == 0:
                return '({})'.format(entity.alias)
            else:
                return '({}:{})'.format(entity.alias, ':'.join(entity.labels))
        elif entity.is_edge():
            _from = hydrage_entity(entity.node_from)
            _to = hydrage_entity(entity.node_to)

            if entity.type is None:
                _rel = '[{}]'.format(entity.alias)
            else:
                _rel = '[{}:{}]'.format(entity.alias, entity.type)

            if entity.with_direction:
                tmpl = '{}-{}->{}'
            else:
                tmpl = '{}-{}-{}'

            return tmpl.format(_from, _rel, _to)
        elif entity.is_path():
            raise NotImplementedError('Not support path yet!')
        else:
            raise ValueError

    return ' '.join([
        hydrage_entity(entity) for entity in entities
    ])


def compile_select_clause(gquery):

    def compile(select):
        if isinstance(select, (Aggregation, Func)):
            return select(lookup_field=gquery.context.lookup_field)

        return select.__str__()

    clause_parts = [compile(select) for select in gquery.returns]

    if len(clause_parts) == 0:
        return ','.join([ent.alias for ent in gquery.queryfor])

    return ','.join(clause_parts)


def compile_order_by(gquery):
    if gquery.order_by() is None:
        return ''

    order_by_field = gquery.order_by().strip()

    order_type = 'ASC'
    if order_by_field.startswith('-'):
        order_by_field = order_by_field[1:]
        order_type = 'DESC'

    if len(order_by_field) == 0:
        return ''

    target_field = gquery.context.lookup_field(order_by_field)
    return 'ORDER BY {} {}'.format(target_field, order_type)


def compile(gquery, pretty=False) -> str:
    match_clause = compile_match_clause(*gquery.queryfor)
    where_clause = compile_where_clause(gquery)
    select_clause = compile_select_clause(gquery)

    join_by = '\n' if pretty else ' '

    clause_list = ['MATCH {}'.format(match_clause)]
    if len(where_clause) > 0:
        clause_list.append('WHERE {}'.format(where_clause))

    clause_list.append('RETURN {}'.format(select_clause))
    clause_list.append(compile_order_by(gquery))
    clause_list.append('LIMIT {}'.format(gquery.limit()))

    return join_by.join(filter(lambda clause: len(clause) > 0, clause_list))


# TODO(chuter) cypher escape full support
def _encode_cypher_value(value):
    if isinstance(value, str):
        return '"{}"'.format(value)
    else:
        return value


def _build_node(node):
    key_vals = ','.join(
        ['{}:{}'.format(key, _encode_cypher_value(val)) for key, val in node]
    )

    if len(key_vals) == 0:
        return 'CREATE ({}:{})'.format(node.alias, ':'.join(node.labels))

    return 'CREATE ({}:{} {{{}}})'.format(
        node.alias,
        ':'.join(node.labels),
        key_vals
    )


def _build_relationship(relationship):
    if relationship.type is None:
        raise KeyError('New relationship must with type')

    key_vals = ' '.join([
        '{}:{}'.format(
            key,
            _encode_cypher_value(val)
        ) for key, val in relationship
    ])
    if len(key_vals) == 0:
        return 'CREATE ({})-[{}:{}]->({})'.format(
            relationship.node_from.alias,
            relationship.alias,
            relationship.type,
            relationship.node_to.alias,
        )

    return 'CREATE ({})-[{}:{} {{{}}}]->({})'.format(
        relationship.node_from.alias,
        relationship.alias,
        relationship.type,
        key_vals,
        relationship.node_to.alias,
    )


def build(iterable_nodes, iterable_relationships=[]) -> Iterable:
    nodes_set = set(iterable_nodes)
    for rel in iterable_relationships:
        nodes_set.add(rel.node_from)
        nodes_set.add(rel.node_to)

    relationships_set = set(iterable_relationships)

    create_parts = [_build_node(node) for node in nodes_set]
    create_parts.extend(
        [_build_relationship(rel) for rel in relationships_set]
    )
    return '\n'.join(create_parts)
