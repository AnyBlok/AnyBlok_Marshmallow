# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from . import add_complexe_model, CustomerSchema, AddressSchema, TagSchema
from anyblok_marshmallow import SchemaWrapper, RegistryNotFound
from marshmallow import fields


class TestRegistry(DBTestCase):

    def test_dump_registry_from_context(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema(context={'registry': registry})
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        address = registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(customer)
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

    def test_load_registry_from_context(self):
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
        data = customer_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_validate_registry_from_context(self):
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

    def test_dump_registry_from_init(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema(registry=registry)
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        address = registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(customer)
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

    def test_load_registry_from_init(self):
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
        customer_schema = CustomerSchema(registry=registry)
        data = customer_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_validate_registry_from_init(self):
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
        customer_schema = CustomerSchema(registry=registry)
        errors = customer_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_dump_registry_from_call(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema()
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        address = registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(customer, registry=registry)
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

    def test_load_registry_from_call(self):
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
        customer_schema = CustomerSchema()
        data = customer_schema.load(dump_data, registry=registry)
        self.assertEqual(data, dump_data)

    def test_validate_registry_from_call(self):
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
        customer_schema = CustomerSchema()
        errors = customer_schema.validate(dump_data, registry=registry)
        self.assertFalse(errors)

    def test_dump_registry_from_meta(self):
        registry = self.init_registry(add_complexe_model)
        self.registry = registry

        class CustomerSchema(SchemaWrapper):
            model = 'Model.Customer'
            registry = self.registry

            class Schema:
                addresses = fields.Nested(
                    AddressSchema, many=True, exclude=('customer', ))
                tags = fields.Nested(TagSchema, many=True)

        customer_schema = CustomerSchema()
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        address = registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(customer)
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

    def test_load_registry_from_meta(self):
        registry = self.init_registry(add_complexe_model)
        self.registry = registry

        class CustomerSchema(SchemaWrapper):
            model = 'Model.Customer'
            registry = self.registry

            class Schema:
                addresses = fields.Nested(
                    AddressSchema, many=True, exclude=('customer', ))
                tags = fields.Nested(TagSchema, many=True)

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
        customer_schema = CustomerSchema()
        data = customer_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_validate_registry_from_meta(self):
        registry = self.init_registry(add_complexe_model)
        self.registry = registry

        class CustomerSchema(SchemaWrapper):
            model = 'Model.Customer'
            registry = self.registry

            class Schema:
                addresses = fields.Nested(
                    AddressSchema, many=True, exclude=('customer', ))
                tags = fields.Nested(TagSchema, many=True)

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
        customer_schema = CustomerSchema()
        errors = customer_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_dump_without_registry(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema()
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        with self.assertRaises(RegistryNotFound):
            customer_schema.dump(customer)

    def test_load_without_registry(self):
        self.init_registry(add_complexe_model)
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
        customer_schema = CustomerSchema()
        with self.assertRaises(RegistryNotFound):
            customer_schema.load(dump_data)

    def test_validate_without_registry(self):
        self.init_registry(add_complexe_model)
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
        customer_schema = CustomerSchema()
        with self.assertRaises(RegistryNotFound):
            customer_schema.validate(dump_data)
