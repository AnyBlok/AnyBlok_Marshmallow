# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_marshmallow import ModelSchema
from anyblok_marshmallow.fields import Nested, File
from anyblok import Declarations
from anyblok.column import Integer, LargeBinary, Selection
from anyblok.field import Function
from os import urandom
from base64 import b64encode


class TestField(DBTestCase):

    def add_field_function(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)
            name = Function(fget='_get_name')

            def _get_name(self):
                return 'test'

    def add_field_largebinary(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)
            file = LargeBinary()

    def add_field_selection_with_object(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)
            name = Selection(selections={'foo': 'bar', 'bar': 'foo'},
                             default='foo')

    def add_field_selection_with_classmethod(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)
            name = Selection(selections='get_modes', default='foo')

            @classmethod
            def get_modes(cls):
                return {'foo': 'bar', 'bar': 'foo'}

    def test_dump_function(self):
        registry = self.init_registry(self.add_field_function)
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})

        exemple = registry.Exemple.insert()
        data, errors = exemple_schema.dump(exemple)
        self.assertFalse(errors)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'name': 'test',
            }
        )

    def test_load_function(self):
        registry = self.init_registry(self.add_field_function)
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        data, errors = exemple_schema.load(dump_data)
        self.assertEqual(data, dump_data)
        self.assertFalse(errors)

    def test_validate_function(self):
        registry = self.init_registry(self.add_field_function)
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        errors = exemple_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_dump_selection_with_object(self):
        registry = self.init_registry(self.add_field_selection_with_object)
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})

        exemple = registry.Exemple.insert()
        data, errors = exemple_schema.dump(exemple)
        self.assertFalse(errors)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'name': 'foo',
            }
        )

    def test_load_selection_with_object_ok(self):
        registry = self.init_registry(self.add_field_selection_with_object)
        dump_data = {
            'id': 1,
            'name': 'foo',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        data, errors = exemple_schema.load(dump_data)
        self.assertEqual(data, dump_data)
        self.assertFalse(errors)

    def test_load_selection_with_object_ko(self):
        registry = self.init_registry(self.add_field_selection_with_object)
        dump_data = {
            'id': 1,
            'name': 'wrong_value',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        data, errors = exemple_schema.load(dump_data)
        self.assertEqual(errors, {'name': ['Not a valid choice.']})

    def test_validate_selection_with_object_ok(self):
        registry = self.init_registry(self.add_field_selection_with_object)
        dump_data = {
            'id': 1,
            'name': 'foo',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        errors = exemple_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_validate_selection_with_object_ko(self):
        registry = self.init_registry(self.add_field_selection_with_object)
        dump_data = {
            'id': 1,
            'name': 'wrong_value',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        errors = exemple_schema.validate(dump_data)
        self.assertEqual(errors, {'name': ['Not a valid choice.']})

    def test_dump_selection_with_classmethod(self):
        registry = self.init_registry(self.add_field_selection_with_classmethod)
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})

        exemple = registry.Exemple.insert()
        data, errors = exemple_schema.dump(exemple)
        self.assertFalse(errors)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'name': 'foo',
            }
        )

    def test_load_selection_with_classmethod_ok(self):
        registry = self.init_registry(self.add_field_selection_with_classmethod)
        dump_data = {
            'id': 1,
            'name': 'foo',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        data, errors = exemple_schema.load(dump_data)
        self.assertEqual(data, dump_data)
        self.assertFalse(errors)

    def test_load_selection_with_classmethod_ko(self):
        registry = self.init_registry(self.add_field_selection_with_classmethod)
        dump_data = {
            'id': 1,
            'name': 'wrong_value',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        data, errors = exemple_schema.load(dump_data)
        self.assertEqual(errors, {'name': ['Not a valid choice.']})

    def test_validate_selection_with_classmethod_ok(self):
        registry = self.init_registry(self.add_field_selection_with_classmethod)
        dump_data = {
            'id': 1,
            'name': 'foo',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        errors = exemple_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_validate_selection_with_classmethod_ko(self):
        registry = self.init_registry(self.add_field_selection_with_classmethod)
        dump_data = {
            'id': 1,
            'name': 'wrong_value',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        errors = exemple_schema.validate(dump_data)
        self.assertEqual(errors, {'name': ['Not a valid choice.']})

    def getExempleSchema(self):

        class Exemple2Schema(ModelSchema):

            class Meta:
                model = 'Model.Exemple2'

        class ExempleSchema(ModelSchema):

            exemple2 = Nested(Exemple2Schema(only=('id',)))

            class Meta:
                model = 'Model.Exemple'

        return ExempleSchema

    def getExemple2Schema(self):

        class ExempleSchema(ModelSchema):

            class Meta:
                model = 'Model.Exemple'

        class Exemple2Schema(ModelSchema):

            exemple = Nested(ExempleSchema(only=('id',)))

            class Meta:
                model = 'Model.Exemple2'

        return Exemple2Schema

    def getExempleSchemaLO(self):

        class ExempleSchema(ModelSchema):

            file = File()

            class Meta:
                model = 'Model.Exemple'

        return ExempleSchema

    def test_dump_file(self):
        registry = self.init_registry(self.add_field_largebinary)
        exemple_schema = self.getExempleSchemaLO()(registry=registry)
        file_ = urandom(100)
        exemple = registry.Exemple.insert(file=file_)
        data, errors = exemple_schema.dump(exemple)
        self.assertFalse(errors)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'file': b64encode(file_).decode('utf-8'),
            }
        )

    def test_load_file(self):
        registry = self.init_registry(self.add_field_function)
        file_ = urandom(100)
        dump_data = {
            'id': 1,
            'file': b64encode(file_).decode('utf-8'),
        }
        exemple_schema = self.getExempleSchemaLO()(registry=registry)
        data, errors = exemple_schema.load(dump_data)
        self.assertEqual(data, {'id': 1, 'file': file_})
        self.assertFalse(errors)

    def test_validate_file(self):
        registry = self.init_registry(self.add_field_function)
        file_ = urandom(100)
        dump_data = {
            'id': 1,
            'file': b64encode(file_).decode('utf-8'),
        }
        exemple_schema = self.getExempleSchemaLO()(registry=registry)
        errors = exemple_schema.validate(dump_data)
        self.assertFalse(errors)
