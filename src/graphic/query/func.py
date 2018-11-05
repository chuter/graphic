#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from typing import Any
from six import add_metaclass

from graphic.compat import is_py37


class FuncMeta(type):
    __slots__ = ()
    _name_2_func_class = {}

    def __init__(cls, name, bases, attrs, **kwargs):
        super(FuncMeta, cls).__init__(name, bases, attrs, **kwargs)

        if name in ['Func', 'Aggregation']:
            return

        func_names = [
            lambda name: name.strip() for name in attrs.get('_name', '').split(
                ','
            )
        ]
        func_names.append(name.lower())

        for _name in func_names:
            cls._name_2_func_class[_name] = cls

    @classmethod
    def get_func(cls, name):
        return cls._name_2_func_class.get(name, None)


@add_metaclass(FuncMeta)
class Func:

    __slots__ = ()

    def __new__(cls, field_str, val, *args, **kwargs):
        func = object.__new__(cls)
        func._field = field_str
        func._val = val
        return func

    def __call__(self, lookup_field=None) -> str:
        _field = self._field
        if lookup_field is not None:
            _field = lookup_field(_field)

        return '{}{}{!r}'.format(
            _field,
            self.exp,
            self._val
        )

    def __deepcopy__(self, memodict):
        return type(self)(self._field, self._val)

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '{}({}, {!r})'.format(
            self.__class__.__name__,
            self._field,
            self._val
        )


__funcs__ = (('eq', '='), ('gt', '>'), ('lt', '<'), ('gte', '>='),
             ('lte', '<='), ('neq', '<>'), ('in', ' IN '),
             ('startswith', ' STARTS WITH '), ('endswith', ' ENDS WITH '),
             ('contains', ' CONTAINS '))


for name, exp in __funcs__:
    _ = type(name, (Func, ), {
        "__slots__": ('_field', '_val', ),
        "exp": exp,
    })


@add_metaclass(FuncMeta)
class Aggregation:

    __slots__ = ()

    def __new__(cls, field_str, *args, **kwargs):
        func = object.__new__(cls)
        func._field = field_str
        return func

    def __call__(self, lookup_field=None) -> str:
        _field = self._field
        if lookup_field is not None:
            _field = lookup_field(_field)

        return '{}({})'.format(
            self.__class__.__name__,
            _field
        )

    def __deepcopy__(self, memodict):
        return type(self)(self._field, self._val)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            self._field,
        )


__aggregations__ = ('avg', 'min', 'max', 'sum', 'count')


for name in __aggregations__:
    _ = type(name, (Aggregation, ), {
        "__slots__": ('_field', )
    })


lookup_func = Func.get_func


def __getattr__(name: str) -> Any:
    target = lookup_func(name)
    if target is None:
        raise AttributeError

    return target


if not is_py37():
    from itertools import chain

    _all_opr_func_names = map(lambda opfunc: opfunc[0], __funcs__)

    for reg_func in chain(_all_opr_func_names, __aggregations__):
        locals()[reg_func] = lookup_func(reg_func)
