#!/usr/bin/env python
# -*- encoding: utf-8 -*-


# flake8: noqa


import graphic


class TestGraphic:

    def test_interface_design_for_build():
        local_graph = graphic.graph(
            # node, ...
            # edge, ...
            # path, ...
        )
        # iterable for nodes, edges, pathes

        local_graph.node() | .edge | .path  # create node, edge, path
        local_graph.add()  # [collection] node, edge, path

        path.in_from(node)
        path.out_to(node)

        .diedge()  # with direction edge

    def test_interface_design_for_read():
        remote_graph = graphic.use_neo4j('graph_name', **credits)

        query._as('another_query_label')(
            node | edge | (diedge & path),
            optional=True
        )  # query object

        query.select(
            'a.uid',
            alias(count('a'))  # min, avg, sum, max ...
        )

        query = query | query & query

        query.filter.for('[node, edge, path]')(
           _ ref to 'query_label.[node, edge, path]'
           eq(_) | contians() & ...
        ).filter.for(...)(...)

        query.group_by()

        query.order_by().limit()

        graph = remote_graph.fetch(query, () => {})
        graph + - graph

        remote_graph.delete(query | local_graph)
        remote_graph.push(local_graph, (each) => {}, ) -> graph

        graph.pushto(remote_graph, on_create=cb_func, on_get=cb_func)

    def test_interface_for_process_graph():
        proc_pipeline = pipeline(
            source=local_graph or reader
            is_streaming=True,
            batch_size=10000,
        )
        proc_pipeline.append(
            etl('', **properties)
        ).append(
            algos('page_rank', **properties)
        ).append(
            dataflow('drawer', **properties)
        )

        proc_pipeline.start(
            on_finished=cb,
            on_step_forward=cb,
            on_failure=cb
        )  # aysnc
 