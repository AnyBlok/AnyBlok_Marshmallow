# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_marshmallow import ModelSchema
from anyblok_marshmallow.fields import Nested, File
from anyblok import Declarations
from anyblok.column import Integer, LargeBinary
from anyblok.field import Function
from anyblok.relationship import One2One
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

    def add_field_one2one(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)

        @Declarations.register(Declarations.Model)
        class Exemple2:
            id = Integer(primary_key=True)
            exemple = One2One(model='Model.Exemple', backref='exemple2')

    def add_field_largebinary(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)
            file = LargeBinary()

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

    def test_dump_one2one_1(self):
        registry = self.init_registry(self.add_field_one2one)
        exemple_schema = self.getExempleSchema()(registry=registry)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        data, errors = exemple_schema.dump(exemple)
        self.assertFalse(errors)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'exemple2': {
                    'id': exemple2.id,
                },
            }
        )

    def test_dump_one2one_2(self):
        registry = self.init_registry(self.add_field_one2one)
        exemple2_schema = self.getExemple2Schema()(registry=registry)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        data, errors = exemple2_schema.dump(exemple2)
        self.assertFalse(errors)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'exemple': {
                    'id': exemple.id,
                },
            }
        )

    def test_load_one2one_1(self):
        registry = self.init_registry(self.add_field_one2one)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        dump_data = {
            'id': exemple.id,
            'exemple2': {
                'id': exemple2.id,
            },
        }
        exemple_schema = self.getExempleSchema()(registry=registry)
        data, errors = exemple_schema.load(dump_data)
        self.assertEqual(data, dump_data)
        self.assertFalse(errors)

    def test_load_one2one_2(self):
        registry = self.init_registry(self.add_field_one2one)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        dump_data = {
            'id': exemple2.id,
            'exemple': {
                'id': exemple.id,
            }
        }
        exemple2_schema = self.getExemple2Schema()(registry=registry)
        data, errors = exemple2_schema.load(dump_data)
        self.assertEqual(data, dump_data)
        self.assertFalse(errors)

    def test_validate_one2one_1(self):
        registry = self.init_registry(self.add_field_one2one)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        dump_data = {
            'id': exemple.id,
            'exemple2': {
                'id': exemple2.id,
            },
        }
        exemple_schema = self.getExempleSchema()(registry=registry)
        errors = exemple_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_validate_one2one_2(self):
        registry = self.init_registry(self.add_field_one2one)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        dump_data = {
            'id': exemple2.id,
            'exemple': {
                'id': exemple.id,
            }
        }
        exemple2_schema = self.getExemple2Schema()(registry=registry)
        errors = exemple2_schema.validate(dump_data)
        self.assertFalse(errors)

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
