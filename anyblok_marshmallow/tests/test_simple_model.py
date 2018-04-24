# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from . import add_simple_model, ExempleSchema
from marshmallow.exceptions import ValidationError


class TestSimpleModel(DBTestCase):

    def test_dump_simple_schema(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data = exemple_schema.dump(exemple)
        self.assertEqual(data, {'number': None, 'id': 1, 'name': 'test'})

    def test_load_simple_schema_1(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data = exemple_schema.load({'id': exemple.id, 'name': exemple.name})
        self.assertEqual(data, {'id': exemple.id, 'name': exemple.name})

    def test_load_simple_schema_2(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        with self.assertRaises(ValidationError) as exception:
            exemple_schema.load({'id': exemple.id})

        self.assertEqual(
            exception.exception.messages,
            {'name': ["Missing data for required field."]}
        )

    def test_load_simple_schema_3(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(
            partial=('name',), context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data = exemple_schema.load({'id': exemple.id})
        self.assertEqual(data, {'id': exemple.id})

    def test_load_simple_schema_4(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(
            partial=('name',), context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        with self.assertRaises(ValidationError) as exception:
            exemple_schema.load({'id': exemple.id, 'name': None})

        self.assertEqual(
            exception.exception.messages,
            {'name': ['Field may not be null.']}
        )

    def test_validate_simple_schema(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        errors = exemple_schema.validate(
            {'id': exemple.id, 'name': exemple.name, 'number': 'test'})
        self.assertEqual(errors, {'number': ['Not a valid integer.']})
