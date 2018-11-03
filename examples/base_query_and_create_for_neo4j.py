#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import random
import graphic


# prepare data
# company nodes
cid = 101
company_names = ['BOSS', 'Google', 'Amazon', 'FB', 'Micro Soft', 'Apple',
                 'Salesforce' 'Workday', 'IBM', 'Alibaba', 'Tencent', 'Baidu']


def new_company_node(name):
    global cid

    cid += 1
    return graphic.node('Company', name=name, cid=cid)._as(
        name.replace(' ', '')
    )


company_nodes = [new_company_node(name) for name in company_names]


# geek nodes
gid = 111
geek_names = ['chuter', 'saras', 'magic', 'robert', 'smith', 'david', 'seeman'
              'zn', 'victor', 'Pablo Isla', 'Johan Thijs', 'Jensen Huang']


def new_geek_node(name):
    global gid

    gid += 1
    return graphic.node('Geek', name=name, uid=gid)._as(name.replace(' ', ''))


geek_nodes = [new_geek_node(name) for name in geek_names]


def build_relations(count):
    pairs = []
    for geek in geek_nodes:
        for company in company_nodes:
            pairs.append((geek, company))

    random.shuffle(pairs)
    select_pairs = pairs[:count]

    relationships = []
    for geek, company in select_pairs:
        relationships.append(
            graphic.relationship(geek, company, type='WORKAT')._as(
                'r{}{}'.format(geek.uid, company.cid)
            )
        )
    return relationships


graph = graphic.use_neo4j()
graph.push(*company_nodes, *geek_nodes, *build_relations(20))


query = graphic.relationship(
    graphic.node('Geek')._as('g'),
    graphic.node('Company')._as('c')
).query.limit(30)
result = graph.fetch(query)

local_graph = result.graph

assert len(local_graph.relationships) == 20

for node in local_graph.nodes:
    print(node)

for relation in local_graph.relationships:
    print(relation)
