# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from . import add_complexe_model, CustomerSchema
from anyblok_marshmallow import SchemaWrapper, PostLoadSchema
from marshmallow.exceptions import ValidationError


class ColumnSchema(SchemaWrapper):
    model = "Model.System.Column"

    class Schema(PostLoadSchema):
        pass


class ColumnSchema2(SchemaWrapper):
    model = "Model.System.Column"

    class Schema(PostLoadSchema):
        post_load_attributes = ['model', 'name']


class PostLoadCustomSchema(CustomerSchema):
    class Schema(CustomerSchema.Schema, PostLoadSchema):
        pass


class PostLoadCustomSchema2(CustomerSchema):
    class Schema(CustomerSchema.Schema, PostLoadSchema):
        post_load_attributes = ['name']


class PostLoadCustomSchema3(CustomerSchema):
    class Schema(CustomerSchema.Schema, PostLoadSchema):
        post_load_attributes = ['ko']


class TestPostLoad(DBTestCase):

    def get_customer(self, registry):
        tag = registry.Tag.insert(name="tag 1")
        customer = registry.Customer.insert(name="C1")
        customer.tags.append(tag)
        city = registry.City.insert(name="Rouen", zipcode="76000")
        registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        return customer

    def test_post_load(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = PostLoadCustomSchema()
        customer_schema.context['registry'] = registry

        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer)
        data = customer_schema.load(dump_data)

        self.assertIs(data, customer)
        self.assertEqual(
            repr(data),
            "<Customer(name='C1', tags=[<Tag(name='tag 1')>])>"
        )

    def test_post_load_with_specific_field(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = PostLoadCustomSchema2()
        customer_schema.context['registry'] = registry

        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer)
        data = customer_schema.load(dump_data)

        self.assertIs(data, customer)
        self.assertEqual(
            repr(data),
            "<Customer(name='C1', tags=[<Tag(name='tag 1')>])>"
        )

    def test_post_load_with_specific_field_wrong_field(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = PostLoadCustomSchema3()
        customer_schema.context['registry'] = registry

        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer)
        with self.assertRaises(ValidationError) as exception:
            customer_schema.load(dump_data)

        self.assertEqual(
            exception.exception.messages,
            {
                'KeyError': "'ko' is unknow in the data"
            }
        )

    def test_post_load_with_polymorphism(self):
        registry = self.init_registry(add_complexe_model)
        column_schema = ColumnSchema()
        column_schema.context['registry'] = registry

        column = registry.System.Column.query().first()
        dump_data = column_schema.dump(column)
        data = column_schema.load(dump_data)

        self.assertIs(data, column)

    def test_post_load_return_instance_polymorphic_specific_field(self):
        registry = self.init_registry(add_complexe_model)
        column_schema = ColumnSchema2()
        column_schema.context['registry'] = registry

        column = registry.System.Column.query().first()
        dump_data = column_schema.dump(column)
        data = column_schema.load(dump_data)

        self.assertIs(data, column)

    def test_post_load_no_instance_found(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = PostLoadCustomSchema()
        customer_schema.context['registry'] = registry

        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer)
        dump_data['id'] += 1
        with self.assertRaises(ValidationError) as exception:
            customer_schema.load(dump_data)

        self.assertEqual(
            exception.exception.messages,
            {
                'instance': (
                    "No instance of <class 'anyblok.model.factory."
                    "ModelCustomer'> found with the filter keys ['id']"
                ),
            }
        )

    def test_post_load_with_more_than_one_instance(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = PostLoadCustomSchema2()
        customer_schema.context['registry'] = registry

        self.get_customer(registry)
        customer = self.get_customer(registry)
        dump_data = customer_schema.dump(customer)
        with self.assertRaises(ValidationError) as exception:
            customer_schema.load(dump_data)

        self.assertEqual(
            exception.exception.messages,
            {
                'instance': (
                    "2 instances of <class 'anyblok.model.factory."
                    "ModelCustomer'> found with the filter keys ['name']"
                ),
            }
        )
