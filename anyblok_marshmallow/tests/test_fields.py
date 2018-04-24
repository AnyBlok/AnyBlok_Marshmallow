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
from anyblok_marshmallow.fields import Nested, File, JsonCollection
from marshmallow import fields
from anyblok import Declarations
from anyblok.column import Integer, LargeBinary, Selection, Json, String
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
        data = exemple_schema.dump(exemple)
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
        data = exemple_schema.load(dump_data)
        self.assertEqual(data, dump_data)

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
        data = exemple_schema.dump(exemple)
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
        data = exemple_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_load_selection_with_object_ko(self):
        registry = self.init_registry(self.add_field_selection_with_object)
        dump_data = {
            'id': 1,
            'name': 'wrong_value',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})
        with self.assertRaises(ValidationError) as exception:
            exemple_schema.load(dump_data)

        self.assertEqual(
            exception.exception.messages,
            {'name': ['Not a valid choice.']}
        )

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
        data = exemple_schema.dump(exemple)
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
        data = exemple_schema.load(dump_data)
        self.assertEqual(data, dump_data)

    def test_load_selection_with_classmethod_ko(self):
        registry = self.init_registry(self.add_field_selection_with_classmethod)
        dump_data = {
            'id': 1,
            'name': 'wrong_value',
        }
        exemple_schema = ModelSchema(
            registry=registry, context={'model': "Model.Exemple"})

        with self.assertRaises(ValidationError) as exception:
            exemple_schema.load(dump_data)

        self.assertEqual(
            exception.exception.messages,
            {'name': ['Not a valid choice.']}
        )

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
        data = exemple_schema.dump(exemple)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'file': b64encode(file_).decode('utf-8'),
            }
        )

    def test_dump_file_with_value_is_none(self):
        registry = self.init_registry(self.add_field_largebinary)
        exemple_schema = self.getExempleSchemaLO()(registry=registry)
        exemple = registry.Exemple.insert(file=None)
        data = exemple_schema.dump(exemple)
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'file': None,
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
        data = exemple_schema.load(dump_data)
        self.assertEqual(data, {'id': 1, 'file': file_})

    def test_load_file_with_value_is_none(self):
        registry = self.init_registry(self.add_field_function)
        dump_data = {
            'id': 1,
            'file': '',
        }
        exemple_schema = self.getExempleSchemaLO()(registry=registry)
        data = exemple_schema.load(dump_data)
        self.assertEqual(data, {'id': 1, 'file': None})

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

    def add_field_json_collection_property(self):

        @Declarations.register(Declarations.Model)
        class Exemple:
            id = Integer(primary_key=True)
            properties = Json(default={})

        @Declarations.register(Declarations.Model)
        class Exemple2:
            id = Integer(primary_key=True)
            name = String()

    @property
    def getJsonPropertySchema1(self):

        class JsonCollectionSchema(ModelSchema):
            class Meta:
                model = 'Model.Exemple2'

            name = JsonCollection(fieldname="properties", keys=['name'])

        return JsonCollectionSchema

    def test_json_collection_wrong_field_cls_type(self):
        self.init_registry(self.add_field_json_collection_property)

        with self.assertRaises(ValueError):
            class JsonCollectionSchema(ModelSchema):
                class Meta:
                    model = 'Model.Exemple2'

                name = JsonCollection(
                    fieldname="properties",
                    keys=['name'],
                    cls_or_instance_type=String  # this is an AnyBlok String
                                                 # not a marshmallow String
                )

    def test_json_collection_wrong_field_instance_type(self):
        self.init_registry(self.add_field_json_collection_property)

        with self.assertRaises(ValueError):
            class JsonCollectionSchema(ModelSchema):
                class Meta:
                    model = 'Model.Exemple2'

                name = JsonCollection(
                    fieldname="properties",
                    keys=['name'],
                    cls_or_instance_type=String()  # this is an AnyBlok String
                                                   # not a marshmallow String
                )

    def test_dump_json_collection_list(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple2 = registry.Exemple2.insert(name='foo')
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        data = exemple_schema.dump(
            exemple2,
            instances=dict(default=exemple)
        )
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'name': "foo",
            }
        )

    def test_dump_json_collection_dict(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(
            properties={'name': {'foo': 'Foo', 'bar': 'Bar'}})
        exemple2 = registry.Exemple2.insert(name='foo')
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        data = exemple_schema.dump(
            exemple2,
            instances=dict(default=exemple)
        )
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'name': "foo",
            }
        )

    def test_dump_json_collection_list_with_field_instance(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple2 = registry.Exemple2.insert(name='foo')

        class JsonCollectionSchema(ModelSchema):
            class Meta:
                model = 'Model.Exemple2'

            name = JsonCollection(
                fieldname="properties",
                keys=['name'],
                cls_or_instance_type=fields.String(required=True)
            )

        exemple_schema = JsonCollectionSchema(registry=registry)
        data = exemple_schema.dump(
            exemple2,
            instances=dict(default=exemple)
        )
        self.assertEqual(
            data,
            {
                'id': exemple.id,
                'name': "foo",
            }
        )

    def test_load_json_collection_ok(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'foo'
        }
        data = exemple_schema.load(
            dump_data,
            instances=dict(default=exemple)
        )
        self.assertEqual(data, dump_data)

    def test_load_json_collection_ko_not_a_valid_choice(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'other'
        }
        with self.assertRaises(ValidationError) as exception:
            exemple_schema.load(
                dump_data,
                instances=dict(default=exemple)
            )
        self.assertEqual(
            exception.exception.messages,
            {'name': ['Not a valid choice.']}
        )

    def test_load_json_collection_ko_no_instance(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'other'
        }
        with self.assertRaises(ValidationError) as exception:
            exemple_schema.load(dump_data)
        self.assertEqual(
            exception.exception.messages,
            {
                'name': {
                    'fieldname': (
                        "No fieldname 'properties' found for wanted instance "
                        "name 'default'",
                    ),
                    'instance': (
                        "No instance found for wanted instance name "
                        "'default'",
                    ),
                    'instance values': (
                        "Instance values None is not a dict or list",
                    ),
                },
            })

    def test_load_json_collection_ko_not_a_string(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 3
        }
        with self.assertRaises(ValidationError) as exception:
            exemple_schema.load(
                dump_data,
                instances=dict(default=exemple)
            )
        self.assertEqual(
            exception.exception.messages,
            {'name': ['Not a valid string.']}
        )

    def test_load_json_collection_ko_no_property_values(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(properties={})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'foo'
        }
        with self.assertRaises(ValidationError) as exception:
            exemple_schema.load(
                dump_data,
                instances=dict(default=exemple)
            )
        self.assertEqual(
            exception.exception.messages,
            {
                'name': {
                    'instance values': (
                        'Instance values None is not a dict or list',
                    ),
                },
            },
        )

    def test_validate_json_collection_ok_list(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'foo'
        }
        errors = exemple_schema.validate(
            dump_data,
            instances=dict(default=exemple)
        )
        self.assertFalse(errors)

    def test_validate_json_collection_ok_dict(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(
            properties={'name': {'foo': 'Foo', 'bar': 'Bar'}})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'foo'
        }
        errors = exemple_schema.validate(
            dump_data,
            instances=dict(default=exemple)
        )
        self.assertFalse(errors)

    def test_validate_json_collection_ko_not_a_valid_choice(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'other'
        }
        errors = exemple_schema.validate(
            dump_data,
            instances=dict(default=exemple)
        )
        self.assertEqual(errors, {'name': ['Not a valid choice.']})

    def test_validate_json_collection_ko_no_instance(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'other'
        }
        errors = exemple_schema.validate(dump_data)
        self.assertEqual(
            errors,
            {
                'name': {
                    'fieldname': (
                        "No fieldname 'properties' found for wanted instance "
                        "name 'default'",
                    ),
                    'instance': (
                        "No instance found for wanted instance name "
                        "'default'",
                    ),
                    'instance values': (
                        "Instance values None is not a dict or list",
                    ),
                },
            })

    def test_validate_json_collection_ko_not_a_str(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 3
        }
        errors = exemple_schema.validate(
            dump_data,
            instances=dict(default=exemple)
        )
        self.assertEqual(errors, {'name': ['Not a valid string.']})

    def test_validate_json_collection_ko_no_property_values(self):
        registry = self.init_registry(self.add_field_json_collection_property)
        exemple = registry.Exemple.insert(properties={})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'foo',
        }
        errors = exemple_schema.validate(
            dump_data,
            instances=dict(default=exemple)
        )
        self.assertEqual(
            errors,
            {
                'name': {
                    'instance values': (
                        'Instance values None is not a dict or list',
                    ),
                },
            },
        )

    def test_validate_json_collection_with_multi_instance_ok(self):

        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Exemple1:
                id = Integer(primary_key=True)
                properties1 = Json(default={})

            @Declarations.register(Declarations.Model)
            class Exemple2:
                id = Integer(primary_key=True)
                properties2 = Json(default={})

            @Declarations.register(Declarations.Model)
            class Exemple3:
                id = Integer(primary_key=True)
                name1 = String()
                name2 = String()

        registry = self.init_registry(add_in_registry)
        exemple1 = registry.Exemple1.insert(
            properties1={'sub': {'name': ['foo1', 'bar1']}})
        exemple2 = registry.Exemple2.insert(
            properties2={'sub': {'sub': {
                'name': {'foo2': 'Foo 2', 'bar2': 'Bar 2'}}}})
        exemple3 = registry.Exemple3.insert(name1='foo', name2='foo2')

        class JsonCollectionSchema(ModelSchema):
            class Meta:
                model = 'Model.Exemple3'

            name1 = JsonCollection(
                fieldname="properties1",
                keys=['sub', 'name'],
                instance='theexemple1'
            )
            name2 = JsonCollection(
                fieldname="properties2",
                keys=['sub', 'sub', 'name'],
                instance='theexemple2'
            )

        exemple_schema = JsonCollectionSchema(registry=registry)
        errors = exemple_schema.validate(
            {
                'id': exemple3.id,
                'name1': "foo1",
                'name2': "foo2",
            },
            instances=dict(theexemple1=exemple1, theexemple2=exemple2)
        )
        self.assertFalse(errors)

    def test_validate_json_collection_with_multi_instance_ko(self):

        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Exemple1:
                id = Integer(primary_key=True)
                properties = Json(default={})

            @Declarations.register(Declarations.Model)
            class Exemple2:
                id = Integer(primary_key=True)
                properties = Json(default={})

            @Declarations.register(Declarations.Model)
            class Exemple3:
                id = Integer(primary_key=True)
                name1 = String()
                name2 = String()

        registry = self.init_registry(add_in_registry)
        exemple1 = registry.Exemple1.insert(
            properties={'sub': {'name': ['foo1', 'bar1']}})
        exemple2 = registry.Exemple2.insert(
            properties={'sub': {'sub': {
                'name': {'foo2': 'Foo 2', 'bar2': 'Bar 2'}}}})
        exemple3 = registry.Exemple3.insert(name1='foo', name2='foo2')

        class JsonCollectionSchema(ModelSchema):
            class Meta:
                model = 'Model.Exemple2'

            name1 = JsonCollection(
                fieldname="properties",
                keys=['sub', 'name'],
                instance='exemple1'
            )
            name2 = JsonCollection(
                fieldname="properties",
                keys=['sub', 'sub', 'name'],
                instance='exemple2'
            )

        exemple_schema = JsonCollectionSchema(registry=registry)
        errors = exemple_schema.validate(
            {
                'id': exemple3.id,
                'name1': "foo2",
                'name2': "foo1",
            },
            instances=dict(exemple1=exemple1, exemple2=exemple2)
        )
        self.assertEqual(
            errors,
            {
                'name1': ['Not a valid choice.'],
                'name2': ['Not a valid choice.'],
            }
        )
