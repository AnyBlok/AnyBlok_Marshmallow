#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / Marshmallow api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# noqa
from anyblok.column import Integer, String
from anyblok.relationship import Many2One, Many2Many
from anyblok_marshmallow.fields import Nested
from anyblok_marshmallow.schema import SchemaWrapper


def add_simple_model():

    from anyblok import Declarations

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        name = String(nullable=False)
        number = Integer()


class ExempleSchema(SchemaWrapper):
    model = 'Model.Exemple'


def add_complexe_model():

    from anyblok import Declarations

    @Declarations.register(Declarations.Model)
    class City:
        id = Integer(primary_key=True)
        name = String(nullable=False)
        zipcode = String(nullable=False)

        def __repr__(self):
            return '<City(name={self.name!r})>'.format(self=self)

    @Declarations.register(Declarations.Model)
    class Tag:
        id = Integer(primary_key=True)
        name = String(nullable=False)

        def __repr__(self):
            return '<Tag(name={self.name!r})>'.format(self=self)

    @Declarations.register(Declarations.Model)
    class Customer:
        id = Integer(primary_key=True)
        name = String(nullable=False)
        tags = Many2Many(model=Declarations.Model.Tag)

        def __repr__(self):
            return ('<Customer(name={self.name!r}, '
                    'tags={self.tags!r})>').format(self=self)

    @Declarations.register(Declarations.Model)
    class Address:
        id = Integer(primary_key=True)
        street = String(nullable=False)
        city = Many2One(model=Declarations.Model.City, nullable=False)
        customer = Many2One(
            model=Declarations.Model.Customer, nullable=False,
            one2many="addresses")


class CitySchema(SchemaWrapper):
    model = 'Model.City'


class TagSchema(SchemaWrapper):
    model = 'Model.Tag'


class AddressSchema(SchemaWrapper):
    model = 'Model.Address'

    class Schema:
        city = Nested(CitySchema)


class CustomerSchema(SchemaWrapper):
    model = 'Model.Customer'

    class Schema:
        addresses = Nested(AddressSchema, many=True, exclude=('customer', ))
        tags = Nested(TagSchema, many=True)
