# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from . import add_simple_model, ExempleSchema
from anyblok_marshmallow import SchemaWrapper


class TestRequired(DBTestCase):

    def test_schema_with_required_in_meta(self):
        registry = self.init_registry(add_simple_model)

        class MySchema(SchemaWrapper):
            model = 'Model.Exemple'
            required_fields = True

        exemple_schema = MySchema(registry=registry)
        fields = exemple_schema.schema.fields
        self.assertTrue(fields['id'].required)
        self.assertTrue(fields['name'].required)
        self.assertTrue(fields['number'].required)

    def test_schema_with_required_list_in_meta(self):
        registry = self.init_registry(add_simple_model)

        class MySchema(SchemaWrapper):
            model = 'Model.Exemple'
            required_fields = ['name', 'number']

        exemple_schema = MySchema(registry=registry)
        fields = exemple_schema.schema.fields
        self.assertFalse(fields['id'].required)
        self.assertTrue(fields['name'].required)
        self.assertTrue(fields['number'].required)

    def test_schema_with_required_in_context(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(
            context={'registry': registry, 'required_fields': True})
        fields = exemple_schema.schema.fields
        self.assertTrue(fields['id'].required)
        self.assertTrue(fields['name'].required)
        self.assertTrue(fields['number'].required)

    def test_schema_with_required_list_in_context(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(
            context={'registry': registry,
                     'required_fields': ['name', 'number']})
        fields = exemple_schema.schema.fields
        self.assertFalse(fields['id'].required)
        self.assertTrue(fields['name'].required)
        self.assertTrue(fields['number'].required)

    def test_schema_with_required_in_validate(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        self.assertEqual(
            exemple_schema.validate({'id': 1, 'name': 'test'},
                                    required_fields=True),
            {'number': ['Missing data for required field.']}
        )

    def test_schema_with_required_list_in_validate(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        self.assertEqual(
            exemple_schema.validate({'id': 1, 'name': 'test'},
                                    required_fields=['name', 'number']),
            {'number': ['Missing data for required field.']}
        )
