#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Compile the GQuery instance to string as cypher or graphql etc.

"""

from graphic.query import Q

__all__ = ['compile']


LOOKUP_SPLIT_BY = '__'
DEFAULT_REFTO = '_'


# TODO(chuter) negated query support and cypher escape

# TODO(chuter) kill DRY for field: field parse('user.id', 'user.name', ...)
# filter, select, func, aggregations all need to parse that


def hydrage_q(left_expr, val, context, func_lookup):
    parts = left_expr.split(LOOKUP_SPLIT_BY)

    if len(parts) < 2 or len(parts) > 3:
        raise AttributeError('Not a legal expression: {}'.format(left_expr))

    alias = DEFAULT_REFTO

    if len(parts) == 2:
        field, func_name = parts
    else:
        alias, field, func_name = parts

    if alias not in context:
        raise AttributeError('No such object named {} can reffer to'.format(
            alias
        ))

    target_func = func_lookup(func_name)
    if target_func is None:
        raise ArithmeticError('No such func named {}'.format(func_name))

    return target_func.hydrage(alias, field, val)


def compile_where_clause(func_lookup, gquery):

    def compile_q(q):
        if len(q) == 0:
            return ''

        if isinstance(q, Q) and len(q) > 1:
            join_by = ' {} '.format(q.connector)
            return (
                '({})'.format(
                    join_by.join([compile_q(child) for child in q.children])
                )
            )

        if isinstance(q, tuple):
            left_expr, val = q
        else:
            left_expr, val = q.children[0]
        return hydrage_q(left_expr, val, gquery.context, func_lookup)

    if gquery is None or func_lookup is None:
        raise AttributeError

    return compile_q(gquery.where)


def compile_match_clause(*entities):
    def hydrage_entity(entity):
        if entity.is_node():
            node_labels = entity.labels
            if len(node_labels) == 0:
                return '({})'.format(entity.alias)
            else:
                return '({}:{})'.format(entity.alias, ':'.join(entity.labels))
        else:
            raise NotImplementedError('Not support edge and path yet!')

    return ' '.join([
        hydrage_entity(entity) for entity in entities
    ])


# TODO(chuter) implement and add aggreations support
# only build the default clause: id(${alias})
def compile_select_clause(gquery):
    return ','.join([
        'id({})'.format(ent.alias) for ent in gquery.queryfor
    ])


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

    path_parts = order_by_field.split('.')
    if len(path_parts) > 2:
        raise AttributeError('{} is not a valid order by expression'.format(
            order_by_field
        ))

    if len(path_parts) == 2 and path_parts[1] == 'id':
        order_by_field = 'id({})'.format(path_parts[0])

    return 'ORDER BY {} {}'.format(order_by_field, order_type)


# TODO(chuter) add edge and path support!!!!!
# TODO(chuter) add pagination support!!!
def compile(func_lookup, gquery, pretty=False):
    match_clause = compile_match_clause(*gquery.queryfor)
    where_clause = compile_where_clause(func_lookup, gquery)
    select_clause = compile_select_clause(gquery)

    join_by = '\n' if pretty else ' '

    clause_list = ['MATCH {}'.format(match_clause)]
    if len(where_clause) > 0:
        clause_list.append('WHERE {}'.format(where_clause))

    clause_list.append('RETURN {}'.format(select_clause))
    clause_list.append(compile_order_by(gquery))
    clause_list.append('LIMIT {}'.format(gquery.limit()))

    return join_by.join(filter(lambda clause: len(clause) > 0, clause_list))
