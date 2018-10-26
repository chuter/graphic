#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from six import add_metaclass


class FuncMeta(type):
    __slots__ = ()
    _name_2_func_ins = {}

    def __init__(cls, name, bases, attrs, **kwargs):
        super(FuncMeta, cls).__init__(name, bases, attrs, **kwargs)

        if name == 'Func':
            return

        func_names = [
            lambda name: name.strip() for name in attrs.get('_name', '').split(
                ','
            )
        ]
        func_names.append(name.lower())

        func_ins = cls()
        for _name in func_names:
            cls._name_2_func_ins[_name] = func_ins

    @classmethod
    def get_func(cls, name):
        return cls._name_2_func_ins.get(name, None)


@add_metaclass(FuncMeta)
class Func(object):

    def hydrage(self, alias, field, val):
        raise NotImplementedError


class eq(Func):

    def hydrage(self, alias, field, val):
        if field == 'id':
            return 'id({})={}'.format(alias, val)

        if isinstance(val, str):
            return '{}.{}="{}"'.format(alias, field, val)
        else:
            return '{}.{}={}'.format(alias, field, val)


lookup_func = Func.get_func
