# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from . import add_simple_model, ExempleSchema


class TestSimpleModel(DBTestCase):

    def test_dump_simple_schema(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.dump(exemple)
        self.assertFalse(errors)
        self.assertEqual(data, {'number': None, 'id': 1, 'name': 'test'})

    def test_load_simple_schema_1(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.load(
            {'id': exemple.id, 'name': exemple.name})
        self.assertEqual(data, {'id': exemple.id, 'name': exemple.name})
        self.assertFalse(errors)

    def test_load_simple_schema_2(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.load({'id': exemple.id})
        self.assertEqual(data, {'id': exemple.id})
        self.assertEqual(
            errors, {'name': ["Missing data for required field."]})

    def test_load_simple_schema_3(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(
            partial=('name',), context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.load({'id': exemple.id})
        self.assertFalse(errors)
        self.assertEqual(data, {'id': exemple.id})

    def test_load_simple_schema_4(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(
            partial=('name',), context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.load({'id': exemple.id, 'name': None})
        self.assertEqual(errors, {'name': ['Field may not be null.']})
        self.assertEqual(data, {'id': exemple.id})

    def test_validate_simple_schema(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        errors = exemple_schema.validate(
            {'id': exemple.id, 'name': exemple.name, 'number': 'test'})
        self.assertEqual(errors, {'number': ['Not a valid integer.']})
