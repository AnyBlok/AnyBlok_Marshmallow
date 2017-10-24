# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from unittest import TestCase
from anyblok_marshmallow.schema import update_from_kwargs


class A:

    def __init__(self, v1=None, v2=None):
        self.v1 = v1
        self.v2 = v2

    @update_from_kwargs('v1', 'v2')
    def get_result(self, **kwargs):
        return (self.v1, self.v2, kwargs)

    @update_from_kwargs('v1', 'v2')
    def get_result_with_exception(self, **kwargs):
        raise Exception('An exception')


class TestDecorator(TestCase):

    def test_simple_call(self):
        a = A()
        self.assertEqual(a.get_result(), (None, None, {}))

    def test_delete_during_call_from_kwargs_1(self):
        a = A()
        self.assertEqual(a.get_result(v1='test'), ('test', None, {}))

    def test_delete_during_call_from_kwargs_2(self):
        a = A()
        self.assertEqual(a.get_result(v2='test'), (None, 'test', {}))

    def test_delete_during_call_from_kwargs_3(self):
        a = A()
        self.assertEqual(a.get_result(v3='test'), (None, None, {'v3': 'test'}))

    def test_dont_delete_the_main_kwargs(self):
        a = A()
        kwargs = dict(v1='test v1', v3='test v3')
        self.assertEqual(a.get_result(**kwargs),
                         ('test v1', None, {'v3': 'test v3'}))
        self.assertEqual(kwargs, {'v1': 'test v1', 'v3': 'test v3'})

    def test_keep_the_initial_value(self):
        a = A(v1='test')
        self.assertEqual(a.v1, 'test')
        self.assertEqual(a.get_result(v1='other'), ('other', None, {}))
        self.assertEqual(a.v1, 'test')

    def test_keep_the_initial_value_when_an_exception_has_been_raising(self):
        a = A(v1='test')
        self.assertEqual(a.v1, 'test')
        with self.assertRaises(Exception):
            self.assertEqual(a.get_result_with_exception(v1='other'))

        self.assertEqual(a.v1, 'test')
