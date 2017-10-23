# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok.column import Integer, String
from anyblok.relationship import Many2One, Many2Many
from anyblok_marshmallow import ModelSchema
from marshmallow import fields


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


class CitySchema(ModelSchema):

    class Meta:
        model = 'Model.City'


class TagSchema(ModelSchema):

    class Meta:
        model = 'Model.Tag'


class AddressSchema(ModelSchema):

    city = fields.Nested(CitySchema)

    class Meta:
        model = 'Model.Address'


class CustomerSchema(ModelSchema):

    addresses = fields.Nested(AddressSchema, many=True, exclude=('customer', ))
    tags = fields.Nested(TagSchema, many=True)

    class Meta:
        model = 'Model.Customer'


class TestComplexeSchema(DBTestCase):

    def test_dump_complexe_schema(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema(context={'registry': registry})
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        address = registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data, errors = customer_schema.dump(customer)
        self.assertFalse(errors)
        self.assertEqual(
            data,
            {
                'id': customer.id,
                'name': customer.name,
                'addresses': [
                    {
                        'id': address.id,
                        'street': address.street,
                        'city': {
                            'id': city.id,
                            'name': city.name,
                            'zipcode': city.zipcode,
                        },
                    },
                ],
                'tags': [
                    {
                        'id': tag.id,
                        'name': tag.name,
                    },
                ],
            }
        )

    def test_load_complexe_schema(self):
        registry = self.init_registry(add_complexe_model)
        dump_data = {
            'id': 1,
            'name': 'name',
            'addresses': [
                {
                    'id': 2,
                    'street': 'street',
                    'city': {
                        'id': 3,
                        'name': 'name',
                        'zipcode': 'zipcode',
                    },
                },
            ],
            'tags': [
                {
                    'id': 4,
                    'name': 'name',
                },
            ],
        }
        customer_schema = CustomerSchema(context={'registry': registry})
        data, errors = customer_schema.load(dump_data)
        self.assertEqual(data, dump_data)
        self.assertFalse(errors)

    def test_validate_complexe_schema(self):
        registry = self.init_registry(add_complexe_model)
        dump_data = {
            'id': 1,
            'name': 'name',
            'addresses': [
                {
                    'id': 2,
                    'street': 'street',
                    'city': {
                        'id': 3,
                        'name': 'name',
                        'zipcode': 'zipcode',
                    },
                },
            ],
            'tags': [
                {
                    'id': 4,
                    'name': 'name',
                },
            ],
        }
        customer_schema = CustomerSchema(context={'registry': registry})
        errors = customer_schema.validate(dump_data)
        self.assertFalse(errors)
