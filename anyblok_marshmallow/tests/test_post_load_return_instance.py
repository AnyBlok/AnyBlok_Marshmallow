# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from . import add_complexe_model, CustomerSchema, AddressSchema, TagSchema
from anyblok_marshmallow import ModelSchema
from marshmallow import fields


class ColumnSchema(ModelSchema):

    class Meta:
        model = "Model.System.Column"


class TestPostLoad(DBTestCase):

    def get_customer(self, registry):
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        return customer

    def test_post_load_return_instance_from_context(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema(
            context={'post_load_return_instance': True})
        customer_schema.context['registry'] = registry

        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer).data
        data, errors = customer_schema.load(dump_data)

        self.assertFalse(errors)
        self.assertIs(data, customer)
        self.assertEqual(
            repr(data),
            "<Customer(name='C1', tags=[<Tag(name='tag 1')>])>"
        )

    def test_post_load_return_instance_specific_field(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema(
            context={'post_load_return_instance': ['id']})
        customer_schema.context['registry'] = registry

        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer).data
        data, errors = customer_schema.load(dump_data)

        self.assertFalse(errors)
        self.assertIs(data, customer)
        self.assertEqual(
            repr(data),
            "<Customer(name='C1', tags=[<Tag(name='tag 1')>])>"
        )

    def test_post_load_return_instance_polymorphic(self):
        registry = self.init_registry(add_complexe_model)
        column_schema = ColumnSchema(
            context={'post_load_return_instance': True})
        column_schema.context['registry'] = registry

        column = registry.System.Column.query().first()
        dump_data = column_schema.dump(column).data
        data, errors = column_schema.load(dump_data)

        self.assertFalse(errors)
        self.assertIs(data, column)

    def test_post_load_return_instance_polymorphic_specific_field(self):
        registry = self.init_registry(add_complexe_model)
        column_schema = ColumnSchema(
            context={'post_load_return_instance': ['model', 'name']})
        column_schema.context['registry'] = registry

        column = registry.System.Column.query().first()
        dump_data = column_schema.dump(column).data
        data, errors = column_schema.load(dump_data)

        self.assertFalse(errors)
        self.assertIs(data, column)

    def test_load_post_load_return_instance_from_init(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema(post_load_return_instance=True)
        customer_schema.context['registry'] = registry

        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer).data
        data, errors = customer_schema.load(dump_data)

        self.assertFalse(errors)
        self.assertIs(data, customer)
        self.assertEqual(
            repr(data),
            "<Customer(name='C1', tags=[<Tag(name='tag 1')>])>"
        )

    def test_post_load_return_instance_from_call(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema()
        customer_schema.context['registry'] = registry

        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer).data
        data, errors = customer_schema.load(
            dump_data, post_load_return_instance=True)

        self.assertFalse(errors)
        self.assertIs(data, customer)
        self.assertEqual(
            repr(data),
            "<Customer(name='C1', tags=[<Tag(name='tag 1')>])>"
        )

    def test_post_load_return_instance_from_meta(self):
        registry = self.init_registry(add_complexe_model)

        class CustomerSchema(ModelSchema):

            addresses = fields.Nested(
                AddressSchema, many=True, exclude=('customer', ))
            tags = fields.Nested(TagSchema, many=True)

            class Meta:
                model = 'Model.Customer'
                post_load_return_instance = True

        customer_schema = CustomerSchema()
        customer_schema.context['registry'] = registry
        customer = self.get_customer(registry)

        dump_data = customer_schema.dump(customer).data
        data, errors = customer_schema.load(dump_data)

        self.assertFalse(errors)
        self.assertIs(data, customer)
        self.assertEqual(
            repr(data),
            "<Customer(name='C1', tags=[<Tag(name='tag 1')>])>"
        )

    def test_post_load_return_instance_ko(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema(
            context={'post_load_return_instance': True})
        customer_schema.context['registry'] = registry

        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer).data
        dump_data['id'] += 1
        data, errors = customer_schema.load(dump_data)

        self.assertEqual(
            errors,
            {
                'instance': (
                    "No instance of <class 'anyblok.model.customer'> found "
                    "with the filter keys ['id']"
                ),
            }
        )

    def test_post_load_return_instance_specific_field_ko(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema(
            context={'post_load_return_instance': ['id']})
        customer_schema.context['registry'] = registry

        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer).data
        dump_data['id'] += 1
        data, errors = customer_schema.load(dump_data)

        self.assertEqual(
            errors,
            {
                'instance': (
                    "No instance of <class 'anyblok.model.customer'> found "
                    "with the filter keys ['id']"
                ),
            }
        )

    def test_post_load_return_instance_specific_field_ko_2(self):
        registry = self.init_registry(add_complexe_model)

        class CustomerSchema(ModelSchema):

            class Meta:
                model = 'Model.Customer'

        customer_schema = CustomerSchema(
            context={'post_load_return_instance': ['name']})
        customer_schema.context['registry'] = registry

        self.get_customer(registry)
        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer).data
        data, errors = customer_schema.load(dump_data)

        self.assertEqual(
            errors,
            {
                'instance': (
                    "2 instances of <class 'anyblok.model.customer'> "
                    "found with the filter keys ['name']"
                ),
            }
        )
