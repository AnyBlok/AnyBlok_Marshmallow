# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_marshmallow import SchemaWrapper
from anyblok import Declarations
from anyblok.column import Integer
from anyblok.relationship import One2One, Many2One, Many2Many


class TestRelationShip(DBTestCase):

    def add_field_one2one(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)

        @Declarations.register(Declarations.Model)
        class Exemple2:
            id = Integer(primary_key=True)
            exemple = One2One(model='Model.Exemple', backref='exemple2')

    def add_field_one2many(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)

        @Declarations.register(Declarations.Model)
        class Exemple2:
            id = Integer(primary_key=True)
            exemple = Many2One(model='Model.Exemple', one2many='exemple2')

    def add_field_many2many(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)

        @Declarations.register(Declarations.Model)
        class Exemple2:
            id = Integer(primary_key=True)
            exemple = Many2Many(model='Model.Exemple', many2many='exemple2')

    def getExempleSchema(self):

        class ExempleSchema(SchemaWrapper):
            model = 'Model.Exemple'

        return ExempleSchema

    def getExemple2Schema(self):

        class Exemple2Schema(SchemaWrapper):
            model = 'Model.Exemple2'

        return Exemple2Schema

    def test_dump_one2one_1(self):
        registry = self.init_registry(self.add_field_one2one)
        exemple_schema = self.getExempleSchema()(registry=registry)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        data = exemple_schema.dump(exemple)
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
        data = exemple2_schema.dump(exemple2)
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
        data = exemple_schema.load(dump_data)
        self.assertEqual(data, dump_data)

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
        data = exemple2_schema.load(dump_data)
        self.assertEqual(data, dump_data)

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

    def test_load_one2many(self):
        registry = self.init_registry(self.add_field_one2many)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        dump_data = {
            'id': exemple.id,
            'exemple2': [
                {
                    'id': exemple2.id,
                },
            ],
        }
        exemple_schema = self.getExempleSchema()(registry=registry)
        data = exemple_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_dump_one2many(self):
        registry = self.init_registry(self.add_field_one2many)
        exemple_schema = self.getExempleSchema()(registry=registry)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        data = exemple_schema.dump(exemple)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'exemple2': [
                    {
                        'id': exemple2.id,
                    },
                ],
            }
        )

    def test_validate_one2many(self):
        registry = self.init_registry(self.add_field_one2many)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        dump_data = {
            'id': exemple.id,
            'exemple2': [
                {
                    'id': exemple2.id,
                },
            ],
        }
        exemple_schema = self.getExempleSchema()(registry=registry)
        errors = exemple_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_load_many2one(self):
        registry = self.init_registry(self.add_field_one2many)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        dump_data = {
            'id': exemple2.id,
            'exemple': {
                'id': exemple.id,
            }
        }
        exemple2_schema = self.getExemple2Schema()(registry=registry)
        data = exemple2_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_dump_many2one(self):
        registry = self.init_registry(self.add_field_one2many)
        exemple2_schema = self.getExemple2Schema()(registry=registry)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        data = exemple2_schema.dump(exemple2)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'exemple': {
                    'id': exemple.id,
                },
            }
        )

    def test_validate_many2one(self):
        registry = self.init_registry(self.add_field_one2many)
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

    def test_dump_many2many_1(self):
        registry = self.init_registry(self.add_field_many2many)
        exemple_schema = self.getExempleSchema()(registry=registry)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert()
        exemple2.exemple.append(exemple)
        data = exemple_schema.dump(exemple)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'exemple2': [
                    {
                        'id': exemple2.id,
                    },
                ],
            }
        )

    def test_dump_many2many_2(self):
        registry = self.init_registry(self.add_field_many2many)
        exemple2_schema = self.getExemple2Schema()(registry=registry)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert()
        exemple2.exemple.append(exemple)
        data = exemple2_schema.dump(exemple2)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'exemple': [
                    {
                        'id': exemple.id,
                    },
                ],
            }
        )

    def test_load_many2many_1(self):
        registry = self.init_registry(self.add_field_many2many)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert()
        exemple2.exemple.append(exemple)
        dump_data = {
            'id': exemple.id,
            'exemple2': [
                {
                    'id': exemple2.id,
                },
            ],
        }
        exemple_schema = self.getExempleSchema()(registry=registry)
        data = exemple_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_load_many2many_2(self):
        registry = self.init_registry(self.add_field_many2many)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert()
        exemple2.exemple.append(exemple)
        dump_data = {
            'id': exemple2.id,
            'exemple': [
                {
                    'id': exemple.id,
                },
            ],
        }
        exemple2_schema = self.getExemple2Schema()(registry=registry)
        data = exemple2_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_load_many2many_3(self):
        registry = self.init_registry(self.add_field_many2many)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert()
        exemple2.exemple.append(exemple)
        dump_data = {
            'id': exemple2.id,
            'exemple': exemple,
        }
        exemple2_schema = self.getExemple2Schema()(registry=registry)
        data = exemple2_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_validate_many2many_1(self):
        registry = self.init_registry(self.add_field_many2many)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert()
        exemple2.exemple.append(exemple)
        dump_data = {
            'id': exemple.id,
            'exemple2': [
                {
                    'id': exemple2.id,
                },
            ],
        }
        exemple_schema = self.getExempleSchema()(registry=registry)
        errors = exemple_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_validate_many2many_2(self):
        registry = self.init_registry(self.add_field_many2many)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert()
        exemple2.exemple.append(exemple)
        dump_data = {
            'id': exemple2.id,
            'exemple': [
                {
                    'id': exemple.id,
                },
            ],
        }
        exemple2_schema = self.getExemple2Schema()(registry=registry)
        errors = exemple2_schema.validate(dump_data)
        self.assertFalse(errors)

    def test_validate_many2many_3(self):
        registry = self.init_registry(self.add_field_many2many)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert()
        exemple2.exemple.append(exemple)
        dump_data = {
            'id': exemple2.id,
            'exemple': exemple,
        }
        exemple2_schema = self.getExemple2Schema()(registry=registry)
        errors = exemple2_schema.validate(dump_data)
        self.assertFalse(errors)
