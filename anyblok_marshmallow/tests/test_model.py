# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok_marshmallow import SchemaWrapper, fields
from anyblok.column import Integer, Text
from anyblok import Declarations
from .conftest import init_registry


class AnySchema(SchemaWrapper):
    pass


class TestModelSchema:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_complexe_model):
        transaction = registry_complexe_model.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_dump_model_from_context(self, registry_complexe_model):
        registry = registry_complexe_model
        customer_schema = AnySchema(
            registry=registry, context={'model': "Model.Customer"})
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        address = registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(customer)
        assert (
            data ==
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

    def test_load_model_from_context(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema(
            registry=registry, context={'model': "Model.Customer"})
        data = customer_schema.load(dump_data)
        assert data == dump_data

    def test_validate_model_from_context(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema(
            registry=registry, context={'model': "Model.Customer"})
        errors = customer_schema.validate(dump_data)
        assert not errors

    def test_dump_model_from_init(self, registry_complexe_model):
        registry = registry_complexe_model
        customer_schema = AnySchema(
            registry=registry, model="Model.Customer")
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        address = registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(customer)
        assert (
            data ==
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

    def test_load_model_from_init(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema(
            registry=registry, model="Model.Customer")
        data = customer_schema.load(dump_data)
        assert data == dump_data

    def test_validate_model_from_init(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema(
            registry=registry, model="Model.Customer")
        errors = customer_schema.validate(dump_data)
        assert not errors

    def test_dump_model_from_call(self, registry_complexe_model):
        registry = registry_complexe_model
        customer_schema = AnySchema()
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        address = registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(
            customer, registry=registry, model="Model.Customer")
        assert (
            data ==
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

    def test_load_model_from_call(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema()
        data = customer_schema.load(
            dump_data, registry=registry, model="Model.Customer")
        assert data == dump_data

    def test_validate_model_from_call(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        customer_schema = AnySchema()
        errors = customer_schema.validate(
            dump_data, registry=registry, model="Model.Customer")
        assert not errors

    def test_validate_with_wrong_field(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {
            'id': 1,
            'name': 'test',
            'wrong_field': 'test',
        }
        customer_schema = AnySchema()
        errors = customer_schema.validate(
            dump_data, registry=registry, model="Model.Customer")
        assert (
            "Unknown fields {'wrong_field'} on Model Model.Customer" in
            errors['wrong_field']
        )


class TestModelSchemaSpecCase:

    @pytest.fixture(autouse=True)
    def close_registry(self, request, bloks_loaded):

        def close():
            if hasattr(self, 'registry'):
                self.registry.close()

        request.addfinalizer(close)

    def init_registry(self, *args, **kwargs):
        self.registry = init_registry(*args, **kwargs)
        return self.registry

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
        assert isinstance(field, fields.Text)
