# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_marshmallow import SchemaWrapper
from anyblok_marshmallow.fields import Nested
from anyblok import Declarations
from anyblok.column import Integer, String
from anyblok.relationship import One2One


class TestPolymorphism(DBTestCase):

    def add_field_one2one(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)
            exemple = One2One(model='Model.Exemple', backref='exemple2')
            type = String(nullable=False)

            @classmethod
            def define_mapper_args(cls):
                mapper_args = super(Exemple, cls).define_mapper_args()
                if cls.__registry_name__ == 'Model.Exemple':
                    mapper_args.update({
                        'polymorphic_identity': 'exemple',
                        'polymorphic_on': cls.type,
                    })
                else:
                    mapper_args.update({
                        'polymorphic_identity': 'exemple2',
                    })

                return mapper_args

        @Declarations.register(Declarations.Model)
        class Exemple2(Declarations.Model.Exemple):
            pass

    def getExempleSchema(self):

        class Exemple2Schema(SchemaWrapper):
            model = 'Model.Exemple'

        class ExempleSchema(SchemaWrapper):
            model = 'Model.Exemple'

            class Schema:
                exemple2 = Nested(Exemple2Schema(only=('id',)))
                exemple = Nested(Exemple2Schema(only=('id',)))

        return ExempleSchema

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
                'exemple': None,
                'type': 'exemple',
            }
        )

    def test_dump_one2one_2(self):
        registry = self.init_registry(self.add_field_one2one)
        exemple2_schema = self.getExempleSchema()(registry=registry)
        exemple = registry.Exemple.insert()
        exemple2 = registry.Exemple2.insert(exemple=exemple)
        data = exemple2_schema.dump(exemple2)
        self.assertEqual(
            data,
            {
                'id': exemple2.id,
                'exemple': {
                    'id': exemple.id,
                },
                'exemple2': None,
                'type': 'exemple2',
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
            'type': 'exemple',
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
            },
            'type': 'exemple2',
        }
        exemple2_schema = self.getExempleSchema()(registry=registry)
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
            'type': 'exemple',
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
            },
            'type': 'exemple2',
        }
        exemple2_schema = self.getExempleSchema()(registry=registry)
        errors = exemple2_schema.validate(dump_data)
        self.assertFalse(errors)
