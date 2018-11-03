=========================
Graphic
=========================

|Build Status| |Coverage Status|
=========================================================================


The target of this project is:
**More pythonic, humanize way to play with graph model**

------------

Install
"""""""""""""""""""""""""

.. code-block:: bash

    pip install graphic



Basic Example
"""""""""""""""""""""""""

.. code-block:: python

    >>>from graphic import use_neo4j
    >>>neo4j = use_neo4j()
    >>>boss = graphic.node('Boss', uid=1234)._as('b')
    >>>geek = graphic.node('Geek', uid=2345)._as('g')
    >>>neo4j.push(graphic.relationship(boss, geek, 'WORKTAT', startat=3432432)
    >>>q = graphic.node().filter(id__gt=123).select('id')
    >>>graph = neo4j.fetch()
    >>>from graphic.query.func import avg
    >>>q = graphic.node().select(avg('uid')).order_by('-id').limit(10)



.. |Build Status| image:: https://travis-ci.org/chuter/graphic.svg?branch=master
.. |Coverage Status| image:: https://codecov.io/gh/chuter/graphic/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/chuter/graphic