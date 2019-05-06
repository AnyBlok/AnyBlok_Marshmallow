# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from . import CustomerSchema, AddressSchema, TagSchema
from anyblok_marshmallow import SchemaWrapper
from marshmallow import fields


class TestPrimaryKey:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_complexe_model):
        transaction = registry_complexe_model.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_dump_only_primary_key_from_context(self, registry_complexe_model):
        registry = registry_complexe_model
        customer_schema = CustomerSchema(
            registry=registry, context={'only_primary_key': True})
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(customer)
        assert data == {'id': customer.id}

    def test_load_only_primary_key_from_context(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {'id': 1}
        customer_schema = CustomerSchema(
            registry=registry, context={'only_primary_key': True})
        data = customer_schema.load(dump_data)
        assert data == dump_data

    def test_validate_only_primary_key_from_context(
        self, registry_complexe_model
    ):
        registry = registry_complexe_model
        dump_data = {'id': 1}
        customer_schema = CustomerSchema(
            registry=registry, context={'only_primary_key': True})
        errors = customer_schema.validate(dump_data)
        assert not errors

    def test_dump_only_primary_key_from_init(self, registry_complexe_model):
        registry = registry_complexe_model
        customer_schema = CustomerSchema(
            registry=registry, only_primary_key=True)
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(customer)
        assert data == {'id': customer.id}

    def test_load_only_primary_key_from_init(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {'id': 1}
        customer_schema = CustomerSchema(
            registry=registry, only_primary_key=True)
        data = customer_schema.load(dump_data)
        assert data == dump_data

    def test_validate_only_primary_key_from_init(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {'id': 1}
        customer_schema = CustomerSchema(
            registry=registry, only_primary_key=True)
        errors = customer_schema.validate(dump_data)
        assert not errors

    def test_dump_only_primary_key_from_call(self, registry_complexe_model):
        registry = registry_complexe_model
        customer_schema = CustomerSchema()
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(
            customer, registry=registry, only_primary_key=True)
        assert data == {'id': customer.id}

    def test_load_only_primary_key_from_call(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {'id': 1}
        customer_schema = CustomerSchema()
        data = customer_schema.load(
            dump_data, registry=registry, only_primary_key=True)
        assert data == dump_data

    def test_validate_only_primary_key_from_call(self, registry_complexe_model):
        registry = registry_complexe_model
        dump_data = {'id': 1}
        customer_schema = CustomerSchema()
        errors = customer_schema.validate(
            dump_data, registry=registry, only_primary_key=True)
        assert not errors

    def test_dump_only_primary_key_from_meta(self, registry_complexe_model):
        registry = registry_complexe_model
        self.registry = registry

        class CustomerSchema(SchemaWrapper):
            model = 'Model.Customer'
            registry = self.registry
            only_primary_key = True

            class Schema:
                addresses = fields.Nested(
                    AddressSchema, many=True, exclude=('customer', ))
                tags = fields.Nested(TagSchema, many=True)

        customer_schema = CustomerSchema()
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data = customer_schema.dump(customer)
        assert data == {'id': customer.id}

    def test_load_only_primary_key_from_meta(self, registry_complexe_model):
        registry = registry_complexe_model
        self.registry = registry

        class CustomerSchema(SchemaWrapper):
            model = 'Model.Customer'
            registry = self.registry
            only_primary_key = True

            class Schema:
                addresses = fields.Nested(
                    AddressSchema, many=True, exclude=('customer', ))
                tags = fields.Nested(TagSchema, many=True)

        dump_data = {'id': 1}
        customer_schema = CustomerSchema()
        data = customer_schema.load(dump_data)
        assert data == dump_data

    def test_validate_only_primary_key_from_meta(self, registry_complexe_model):
        registry = registry_complexe_model
        self.registry = registry

        class CustomerSchema(SchemaWrapper):
            model = 'Model.Customer'
            registry = self.registry
            only_primary_key = True

            class Schema:
                addresses = fields.Nested(
                    AddressSchema, many=True, exclude=('customer', ))
                tags = fields.Nested(TagSchema, many=True)

        dump_data = {'id': 1}
        customer_schema = CustomerSchema()
        errors = customer_schema.validate(dump_data)
        assert not errors
