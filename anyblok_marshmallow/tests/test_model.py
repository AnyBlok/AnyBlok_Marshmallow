# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from . import add_complexe_model
from anyblok_marshmallow import SchemaWrapper, fields
from anyblok.column import Integer, Text
from anyblok import Declarations


class AnySchema(SchemaWrapper):
    pass


class TestModelSchema(DBTestCase):

    def test_dump_model_from_context(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = AnySchema(
            registry=registry, context={'model': "Model.Customer"})
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
                    },
                ],
                'tags': [
                    {
                        'id': tag.id,
                    },
                ],
            }
        )

    def test_load_model_from_context(self):
        registry = self.init_registry(add_complexe_model)
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema(
            registry=registry, context={'model': "Model.Customer"})
        data = customer_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_validate_model_from_context(self):
        registry = self.init_registry(add_complexe_model)
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema(
            registry=registry, context={'model': "Model.Customer"})
        errors = customer_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_dump_model_from_init(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = AnySchema(
            registry=registry, model="Model.Customer")
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
                    },
                ],
                'tags': [
                    {
                        'id': tag.id,
                    },
                ],
            }
        )

    def test_load_model_from_init(self):
        registry = self.init_registry(add_complexe_model)
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema(
            registry=registry, model="Model.Customer")
        data = customer_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_validate_model_from_init(self):
        registry = self.init_registry(add_complexe_model)
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema(
            registry=registry, model="Model.Customer")
        errors = customer_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_dump_model_from_call(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = AnySchema()
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        address = registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(
            customer, registry=registry, model="Model.Customer")
        self.assertEqual(
            data,
            {
                'id': customer.id,
                'name': customer.name,
                'addresses': [
                    {
                        'id': address.id,
                    },
                ],
                'tags': [
                    {
                        'id': tag.id,
                    },
                ],
            }
        )

    def test_load_model_from_call(self):
        registry = self.init_registry(add_complexe_model)
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema()
        data = customer_schema.load(
            dump_data, registry=registry, model="Model.Customer")
        self.assertEqual(data, dump_data)

    def test_validate_model_from_call(self):
        registry = self.init_registry(add_complexe_model)
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema()
        errors = customer_schema.validate(
            dump_data, registry=registry, model="Model.Customer")
        self.assertFalse(errors)

    def test_validate_with_wrong_field(self):
        registry = self.init_registry(add_complexe_model)
        dump_data = {
            'id': 1,
            'name': 'test',
            'wrong_field': 'test',
        }
        customer_schema = AnySchema()
        errors = customer_schema.validate(
            dump_data, registry=registry, model="Model.Customer")
        self.assertIn(
            "Unknown fields {'wrong_field'} on Model Model.Customer",
            errors['wrong_field'])

    def test_anyblok_text_is_represented_by_anyblok_marshmallow_text(self):

        def add_in_registry():

            @Declarations.register(Declarations.Model)
            class Exemple:
                id = Integer(primary_key=True)
                name = Text()

        registry = self.init_registry(add_in_registry)

        class ExempleSchema(SchemaWrapper):
            model = 'Model.Exemple'

        schema = ExempleSchema(registry=registry).schema
        field = schema.fields['name']
        self.assertTrue(isinstance(field, fields.Text))
