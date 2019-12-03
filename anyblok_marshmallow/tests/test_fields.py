# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from .conftest import init_registry
from anyblok_marshmallow import SchemaWrapper
from anyblok_marshmallow import fields
from anyblok import Declarations
from anyblok.column import (
    Integer, LargeBinary, Selection, Json, String, Email, URL, UUID,
    PhoneNumber, Country, Color)
from anyblok.field import Function
from os import urandom
from base64 import b64encode
from marshmallow.exceptions import ValidationError
from marshmallow import Schema
from uuid import uuid1
from sqlalchemy_utils import PhoneNumber as PN

try:
    import colour  # noqa
    has_colour = True
except Exception:
    has_colour = False


try:
    import furl  # noqa
    has_furl = True
except Exception:
    has_furl = False


try:
    import phonenumbers  # noqa
    has_phonenumbers = True
except Exception:
    has_phonenumbers = False


try:
    import pycountry  # noqa
    has_pycountry = True
except Exception:
    has_pycountry = False


def add_field_function():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        name = Function(fget='_get_name')

        def _get_name(self):
            return 'test'


@pytest.fixture(scope="class")
def registry_field_function(request, bloks_loaded):
    registry = init_registry(add_field_function)
    request.addfinalizer(registry.close)
    return registry


class TestFieldFunction:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_function):
        transaction = registry_field_function.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_dump_function(self, registry_field_function):
        registry = registry_field_function
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})

        exemple = registry.Exemple.insert()
        data = exemple_schema.dump(exemple)
        assert (
            data ==
            {
                'id': exemple.id,
                'name': 'test',
            }
        )

    def test_load_function(self, registry_field_function):
        registry = registry_field_function
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        data = exemple_schema.load(dump_data)
        assert data == dump_data

    def test_validate_function(self, registry_field_function):
        registry = registry_field_function
        dump_data = {
            'id': 1,
            'name': 'test',
        }
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        errors = exemple_schema.validate(dump_data)
        assert not errors


def add_field_selection_with_object():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        name = Selection(selections={'foo': 'bar', 'bar': 'foo'},
                         default='foo')


@pytest.fixture(scope="class")
def registry_field_selection_with_object(request, bloks_loaded):
    registry = init_registry(add_field_selection_with_object)
    request.addfinalizer(registry.close)
    return registry


class TestFieldSelectionWithObject:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_selection_with_object):
        transaction = registry_field_selection_with_object.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_dump_selection_with_object(
        self, registry_field_selection_with_object
    ):
        registry = registry_field_selection_with_object
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})

        exemple = registry.Exemple.insert()
        data = exemple_schema.dump(exemple)
        assert (
            data ==
            {
                'id': exemple.id,
                'name': 'foo',
            }
        )

    def test_load_selection_with_object_ok(
        self, registry_field_selection_with_object
    ):
        registry = registry_field_selection_with_object
        dump_data = {
            'id': 1,
            'name': 'foo',
        }
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        data = exemple_schema.load(dump_data)
        assert data == dump_data

    def test_load_selection_with_object_ko(
        self, registry_field_selection_with_object
    ):
        registry = registry_field_selection_with_object
        dump_data = {
            'id': 1,
            'name': 'wrong_value',
        }
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(dump_data)

        assert exception._excinfo[1].messages['name'][0].startswith(
            'Must be one of: ')

    def test_validate_selection_with_object_ok(
        self, registry_field_selection_with_object
    ):
        registry = registry_field_selection_with_object
        dump_data = {
            'id': 1,
            'name': 'foo',
        }
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        errors = exemple_schema.validate(dump_data)
        assert not errors

    def test_validate_selection_with_object_ko(
        self, registry_field_selection_with_object
    ):
        registry = registry_field_selection_with_object
        dump_data = {
            'id': 1,
            'name': 'wrong_value',
        }
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        errors = exemple_schema.validate(dump_data)
        assert errors['name'][0].startswith('Must be one of: ')


def add_field_selection_with_classmethod():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        name = Selection(selections='get_modes', default='foo')

        @classmethod
        def get_modes(cls):
            return {'foo': 'bar', 'bar': 'foo'}


@pytest.fixture(scope="class")
def registry_field_selection_with_clssmethod(request, bloks_loaded):
    registry = init_registry(add_field_selection_with_classmethod)
    request.addfinalizer(registry.close)
    return registry


class TestFieldSelectionWithClassmethod:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_selection_with_clssmethod):
        transaction = registry_field_selection_with_clssmethod.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_dump_selection_with_classmethod(
        self, registry_field_selection_with_clssmethod
    ):
        registry = registry_field_selection_with_clssmethod
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})

        exemple = registry.Exemple.insert()
        data = exemple_schema.dump(exemple)
        assert (
            data ==
            {
                'id': exemple.id,
                'name': 'foo',
            }
        )

    def test_load_selection_with_classmethod_ok(
        self, registry_field_selection_with_clssmethod
    ):
        registry = registry_field_selection_with_clssmethod
        dump_data = {
            'id': 1,
            'name': 'foo',
        }
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        data = exemple_schema.load(dump_data)
        assert data == dump_data

    def test_load_selection_with_classmethod_ko(
        self, registry_field_selection_with_clssmethod
    ):
        registry = registry_field_selection_with_clssmethod
        dump_data = {
            'id': 1,
            'name': 'wrong_value',
        }
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})

        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(dump_data)

        assert exception._excinfo[1].messages['name'][0].startswith(
            'Must be one of: ')

    def test_validate_selection_with_classmethod_ok(
        self, registry_field_selection_with_clssmethod
    ):
        registry = registry_field_selection_with_clssmethod
        dump_data = {
            'id': 1,
            'name': 'foo',
        }
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        errors = exemple_schema.validate(dump_data)
        assert not errors

    def test_validate_selection_with_classmethod_ko(
        self, registry_field_selection_with_clssmethod
    ):
        registry = registry_field_selection_with_clssmethod
        dump_data = {
            'id': 1,
            'name': 'wrong_value',
        }
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        errors = exemple_schema.validate(dump_data)
        assert errors['name'][0].startswith('Must be one of: ')


def add_field_largebinary():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        file = LargeBinary()


@pytest.fixture(scope="class")
def registry_field_largebinary(request, bloks_loaded):
    registry = init_registry(add_field_largebinary)
    request.addfinalizer(registry.close)
    return registry


class TestFieldLargeBinary:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_largebinary):
        transaction = registry_field_largebinary.begin_nested()
        request.addfinalizer(transaction.rollback)

    def getExempleSchemaLO(self):

        class ExempleSchema(SchemaWrapper):
            model = 'Model.Exemple'

            class Schema:
                file = fields.File()

        return ExempleSchema

    def test_dump_file(self, registry_field_largebinary):
        registry = registry_field_largebinary
        exemple_schema = self.getExempleSchemaLO()(registry=registry)
        file_ = urandom(100)
        exemple = registry.Exemple.insert(file=file_)
        data = exemple_schema.dump(exemple)
        assert (
            data ==
            {
                'id': exemple.id,
                'file': b64encode(file_).decode('utf-8'),
            }
        )

    def test_dump_file_with_value_is_none(self, registry_field_largebinary):
        registry = registry_field_largebinary
        exemple_schema = self.getExempleSchemaLO()(registry=registry)
        exemple = registry.Exemple.insert(file=None)
        data = exemple_schema.dump(exemple)
        assert (
            data ==
            {
                'id': exemple.id,
                'file': None,
            }
        )

    def test_load_file(self, registry_field_largebinary):
        registry = registry_field_largebinary
        file_ = urandom(100)
        dump_data = {
            'id': 1,
            'file': b64encode(file_).decode('utf-8'),
        }
        exemple_schema = self.getExempleSchemaLO()(registry=registry)
        data = exemple_schema.load(dump_data)
        assert data == {'id': 1, 'file': file_}

    def test_load_file_with_value_is_none(self, registry_field_largebinary):
        registry = registry_field_largebinary
        dump_data = {
            'id': 1,
            'file': '',
        }
        exemple_schema = self.getExempleSchemaLO()(registry=registry)
        data = exemple_schema.load(dump_data)
        assert data == {'id': 1, 'file': None}

    def test_validate_file(self, registry_field_largebinary):
        registry = registry_field_largebinary
        file_ = urandom(100)
        dump_data = {
            'id': 1,
            'file': b64encode(file_).decode('utf-8'),
        }
        exemple_schema = self.getExempleSchemaLO()(registry=registry)
        errors = exemple_schema.validate(dump_data)
        assert not errors


def add_field_json_collection_property():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        properties = Json(default={})

    @Declarations.register(Declarations.Model)
    class Exemple2:
        id = Integer(primary_key=True)
        name = String()


@pytest.fixture(scope="class")
def registry_field_json_collection_property(request, bloks_loaded):
    registry = init_registry(add_field_json_collection_property)
    request.addfinalizer(registry.close)
    return registry


class TestFieldJsonCollectionProperty:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_json_collection_property):
        transaction = registry_field_json_collection_property.begin_nested()
        request.addfinalizer(transaction.rollback)

    @property
    def getJsonPropertySchema1(self):

        class JsonCollectionSchema(SchemaWrapper):
            model = 'Model.Exemple2'

            class Schema:
                name = fields.JsonCollection(
                    fieldname="properties", keys=['name'])

        return JsonCollectionSchema

    def test_json_collection_wrong_field_cls_type(
        self, registry_field_json_collection_property
    ):
        with pytest.raises(ValueError):
            class JsonCollectionSchema(SchemaWrapper):
                model = 'Model.Exemple2'

                class Schema:
                    name = fields.JsonCollection(
                        fieldname="properties",
                        keys=['name'],
                        cls_or_instance_type=String  # this is an AnyBlok String
                                                     # not a marshmallow String
                    )

    def test_json_collection_wrong_field_instance_type(
        self, registry_field_json_collection_property
    ):
        with pytest.raises(ValueError):
            class JsonCollectionSchema(SchemaWrapper):
                model = 'Model.Exemple2'

                class Schema:
                    name = fields.JsonCollection(
                        fieldname="properties",
                        keys=['name'],
                        cls_or_instance_type=String()
                        # this is an AnyBlok String
                        # not a marshmallow String
                    )

    def test_dump_json_collection_list(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple2 = registry.Exemple2.insert(name='foo')
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        data = exemple_schema.dump(
            exemple2,
            instances=dict(default=exemple)
        )
        assert (
            data ==
            {
                'id': exemple.id,
                'name': "foo",
            }
        )

    def test_dump_json_collection_dict(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
        exemple = registry.Exemple.insert(
            properties={'name': {'foo': 'Foo', 'bar': 'Bar'}})
        exemple2 = registry.Exemple2.insert(name='foo')
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        data = exemple_schema.dump(
            exemple2,
            instances=dict(default=exemple)
        )
        assert (
            data ==
            {
                'id': exemple.id,
                'name': "foo",
            }
        )

    def test_dump_json_collection_list_with_field_instance(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple2 = registry.Exemple2.insert(name='foo')

        class JsonCollectionSchema(SchemaWrapper):
            model = 'Model.Exemple2'

            class Schema:
                name = fields.JsonCollection(
                    fieldname="properties",
                    keys=['name'],
                    cls_or_instance_type=fields.String(required=True)
                )

        exemple_schema = JsonCollectionSchema(registry=registry)
        data = exemple_schema.dump(
            exemple2,
            instances=dict(default=exemple)
        )
        assert (
            data ==
            {
                'id': exemple.id,
                'name': "foo",
            }
        )

    def test_load_json_collection_ok(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
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
        assert data == dump_data

    def test_load_json_collection_ko_not_a_valid_choice(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'other'
        }
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(
                dump_data,
                instances=dict(default=exemple)
            )
        assert exception._excinfo[1].messages['name'][0].startswith(
            'Must be one of: ')

    def test_load_json_collection_ko_no_instance(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'other'
        }
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(dump_data)
        assert (
            exception._excinfo[1].messages ==
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

    def test_load_json_collection_ko_not_a_string(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
        exemple = registry.Exemple.insert(properties={'name': ['foo', 'bar']})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 3
        }
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(
                dump_data,
                instances=dict(default=exemple)
            )
        assert (
            exception._excinfo[1].messages ==
            {'name': ['Not a valid string.']}
        )

    def test_load_json_collection_ko_no_property_values(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
        exemple = registry.Exemple.insert(properties={})
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'foo'
        }
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(
                dump_data,
                instances=dict(default=exemple)
            )
        assert (
            exception._excinfo[1].messages ==
            {
                'name': {
                    'instance values': (
                        'Instance values None is not a dict or list',
                    ),
                },
            }
        )

    def test_validate_json_collection_ok_list(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
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
        assert not errors

    def test_validate_json_collection_ok_dict(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
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
        assert not errors

    def test_validate_json_collection_ko_not_a_valid_choice(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
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
        assert errors['name'][0].startswith('Must be one of: ')

    def test_validate_json_collection_ko_no_instance(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
        exemple_schema = self.getJsonPropertySchema1(registry=registry)
        dump_data = {
            'id': 1,
            'name': 'other'
        }
        errors = exemple_schema.validate(dump_data)
        assert (
            errors ==
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

    def test_validate_json_collection_ko_not_a_str(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
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
        assert errors == {'name': ['Not a valid string.']}

    def test_validate_json_collection_ko_no_property_values(
        self, registry_field_json_collection_property
    ):
        registry = registry_field_json_collection_property
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
        assert (
            errors ==
            {
                'name': {
                    'instance values': (
                        'Instance values None is not a dict or list',
                    ),
                },
            }
        )


class TestFieldJsonCollectionProperty2:

    @pytest.fixture(autouse=True)
    def close_registry(self, request, bloks_loaded):

        def close():
            if hasattr(self, 'registry'):
                self.registry.close()

        request.addfinalizer(close)

    def init_registry(self, *args, **kwargs):
        self.registry = init_registry(*args, **kwargs)
        return self.registry

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

        class JsonCollectionSchema(SchemaWrapper):
            model = 'Model.Exemple3'

            class Schema:
                name1 = fields.JsonCollection(
                    fieldname="properties1",
                    keys=['sub', 'name'],
                    instance='theexemple1'
                )
                name2 = fields.JsonCollection(
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
        assert not errors

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

        class JsonCollectionSchema(SchemaWrapper):
            model = 'Model.Exemple2'

            class Schema:
                name1 = fields.JsonCollection(
                    fieldname="properties",
                    keys=['sub', 'name'],
                    instance='exemple1'
                )
                name2 = fields.JsonCollection(
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
        assert errors['name1'][0].startswith('Must be one of: ')
        assert errors['name2'][0].startswith('Must be one of: ')


def add_field_email():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        email = Email()


@pytest.fixture(scope="class")
def registry_field_email(request, bloks_loaded):
    registry = init_registry(add_field_email)
    request.addfinalizer(registry.close)
    return registry


class TestFieldEmail:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_email):
        transaction = registry_field_email.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_email_field_type(self, registry_field_email):
        registry = registry_field_email
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        assert (
            isinstance(exemple_schema.schema.fields['email'], fields.Email))

    def test_dump_email(self, registry_field_email):
        registry = registry_field_email
        exemple = registry.Exemple.insert(email='jssuzanne@anybox.fr')
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        data = exemple_schema.dump(exemple)
        assert (
            data ==
            {
                'id': exemple.id,
                'email': "jssuzanne@anybox.fr",
            }
        )

    def test_email_with_a_valid_email(self, registry_field_email):
        registry = registry_field_email
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'email': 'jssuzanne@anybox.fr'
        }
        load_data = exemple_schema.load(dump_data)
        assert dump_data == load_data

    def test_email_with_an_invalid_email(self, registry_field_email):
        registry = registry_field_email
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'email': 'jssuzanne'
        }
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(dump_data)

        assert (
            exception._excinfo[1].messages ==
            {'email': ['Not a valid email address.']}
        )


def add_field_uuid():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        uuid = UUID()


@pytest.fixture(scope="class")
def registry_field_uuid(request, bloks_loaded):
    registry = init_registry(add_field_uuid)
    request.addfinalizer(registry.close)
    return registry


class TestFieldUuid:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_uuid):
        transaction = registry_field_uuid.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_uuid_field_type(self, registry_field_uuid):
        registry = registry_field_uuid
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        assert (
            isinstance(exemple_schema.schema.fields['uuid'], fields.UUID))

    def test_dump_uuid(self, registry_field_uuid):
        registry = registry_field_uuid
        uuid = uuid1()
        exemple = registry.Exemple.insert(uuid=uuid)
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        data = exemple_schema.dump(exemple)
        assert data == {'id': exemple.id, 'uuid': str(uuid)}

    def test_uuid_with_a_valid_uuid(self, registry_field_uuid):
        registry = registry_field_uuid
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        uuid = uuid1()
        dump_data = {
            'id': 1,
            'uuid': str(uuid)
        }
        load_data = exemple_schema.load(dump_data)
        assert load_data == {'id': 1, 'uuid': uuid}

    def test_uuid_with_an_invalid_uuid(self, registry_field_uuid):
        registry = registry_field_uuid
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'uuid': 'jssuzanne'
        }
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(dump_data)

        assert (
            exception._excinfo[1].messages ==
            {'uuid': ['Not a valid UUID.']}
        )


def add_field_instance_with_object():

    @Declarations.register(Declarations.Model)
    class Records:
        id = Integer(primary_key=True)
        uuid = UUID(default=uuid1)
        code = String()
        number = Integer()


@pytest.fixture(scope="class")
def registry_field_instance(request, bloks_loaded):
    registry = init_registry(add_field_instance_with_object)
    request.addfinalizer(registry.close)
    return registry


class TestFieldInstance:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_instance):
        transaction = registry_field_instance.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_instance_field_str(self, registry_field_instance):
        registry = registry_field_instance
        registry.Records.insert(code="code")

        class TestSchema(Schema):
            code = fields.InstanceField(
                     cls_or_instance_type=fields.Str(),
                     model='Model.Records', key='code')

        sch = TestSchema(context={"registry": registry})

        valid = sch.load(dict(code="code"))
        assert (
            valid ==
            dict(code="code")
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(code="unexisting"))

        assert 'code' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get(
                'code')[0].startswith("Record with")
        )
        assert (
            "'unexisting'" in exception._excinfo[1].messages.get('code')[0]
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(code=666))

        assert 'code' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('code')[0] ==
            "Not a valid string."
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(code=uuid1()))

        assert 'code' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('code')[0] ==
            "Not a valid string."
        )

    def test_instance_field_list_str(self, registry_field_instance):
        registry = registry_field_instance
        for i in range(2):
            registry.Records.insert(code="code%s" % i, number=i)

        class TestSchema(Schema):
            code = fields.InstanceField(
                        cls_or_instance_type=fields.List(fields.Str()),
                        model='Model.Records', key='code')

        sch = TestSchema(context={"registry": registry})

        valid = sch.load(dict(code=["code0", "code1"]))
        assert (
            valid ==
            dict(code=["code0", "code1"])
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(code=["code0", "code1", "code2"]))

        assert 'code' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get(
                'code')[0].startswith("Records with")
        )
        assert "'code2'" in exception._excinfo[1].messages.get('code')[0]

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(code=["code0", 666]))

        assert 'code' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('code').get(1)[0] ==
            "Not a valid string."
        )

    def test_instance_field_other_types(self, registry_field_instance):
        registry = registry_field_instance
        record = registry.Records.insert(number=100)

        class TestSchema(Schema):
            uuid = fields.InstanceField(
                     cls_or_instance_type=fields.UUID(),
                     model='Model.Records', key='uuid')
            number = fields.InstanceField(
                     cls_or_instance_type=fields.Int(),
                     model='Model.Records', key='number')

        sch = TestSchema(context={"registry": registry})

        valid_uuid = sch.load(dict(uuid=record.uuid))

        assert valid_uuid == dict(uuid=record.uuid)

        unexisting_uuid = uuid1()
        with pytest.raises(ValidationError) as exception:
            sch.load(dict(uuid=unexisting_uuid))

        assert 'uuid' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get(
                'uuid')[0].startswith("Record with")
        )
        assert (
            str(unexisting_uuid) in
            exception._excinfo[1].messages.get('uuid')[0]
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(uuid=666))

        assert 'uuid' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('uuid')[0] ==
            "Not a valid UUID."
        )

        valid_number = sch.load(dict(number=record.number))

        assert valid_number == dict(number=record.number)

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(number="Nan"))

        assert 'number' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('number')[0] ==
            "Not a valid integer."
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(number=666))

        assert 'number' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get(
                'number')[0].startswith("Record with")
        )
        assert (
            repr(666) in exception._excinfo[1].messages.get('number')[0]
        )

    def test_instance_field_list_other_types(self, registry_field_instance):
        registry = registry_field_instance
        valid_uuids = []
        for i in range(1, 3):
            rec = registry.Records.insert(number=i*100)
            valid_uuids.append(rec.uuid)

        class TestSchema(Schema):
            uuid = fields.InstanceField(
                        cls_or_instance_type=fields.List(fields.UUID()),
                        model='Model.Records', key='uuid')
            number = fields.InstanceField(
                        cls_or_instance_type=fields.List(fields.Int()),
                        model='Model.Records', key='number')

        sch = TestSchema(context={"registry": registry})
        valid = sch.load(dict(uuid=valid_uuids))
        assert valid == dict(uuid=valid_uuids)

        invalid_uuids = [uuid1(), uuid1()]
        with pytest.raises(ValidationError) as exception:
            sch.load(dict(uuid=invalid_uuids))

        assert 'uuid' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get(
                'uuid')[0].startswith("Records with")
        )
        assert (
            repr(invalid_uuids) in exception._excinfo[1].messages.get('uuid')[0]
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(uuid=[valid_uuids[0], 666]))

        assert 'uuid' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('uuid')[1][0] ==
            "Not a valid UUID."
        )

        valid_numbers = sch.load(dict(number=[100, 200]))
        assert valid_numbers == dict(number=[100, 200])

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(number=[666, 999]))

        assert 'number' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get(
                'number')[0].startswith("Records with")
        )
        assert (
            repr([666, 999]) in exception._excinfo[1].messages.get('number')[0]
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(number=["NAN", 666]))

        assert 'number' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('number')[0][0] ==
            "Not a valid integer."
        )

    def test_instance_field_no_records(self, registry_field_instance):
        registry = registry_field_instance
        for i in range(2):
            registry.Records.insert(code="code%s" % i, number=i)

        class TestSchema(Schema):
            code = fields.InstanceField(
                        cls_or_instance_type=fields.Str(),
                        model='Model.Records', key='code')
            number = fields.InstanceField(
                        cls_or_instance_type=fields.List(fields.Int()),
                        model='Model.Records', key='number')

        sch = TestSchema(context={"registry": registry})

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(code=None))

        assert 'code' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('code')[0] ==
            "Field may not be null."
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(code=""))

        assert 'code' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('code')[0] ==
            "Field may not be null."
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(number=[None]))

        assert 'number' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('number')[0][0] ==
            "Field may not be null."
        )

        with pytest.raises(ValidationError) as exception:
            sch.load(dict(number=[""]))

        assert 'number' in exception._excinfo[1].messages.keys()
        assert (
            exception._excinfo[1].messages.get('number')[0][0] ==
            "Not a valid integer."
        )


def add_field_url():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        url = URL()


@pytest.fixture(scope="class")
def registry_field_url(request, bloks_loaded):
    registry = init_registry(add_field_url)
    request.addfinalizer(registry.close)
    return registry


@pytest.mark.skipif(not has_furl, reason="furl is not installed")
class TestFieldUrl:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_url):
        transaction = registry_field_url.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_url_field_type(self, registry_field_url):
        registry = registry_field_url
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        assert (
            isinstance(exemple_schema.schema.fields['url'], fields.URL))

    def test_dump_url(self, registry_field_url):
        registry = registry_field_url
        exemple = registry.Exemple.insert(url='https://doc.anyblok.org')
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        data = exemple_schema.dump(exemple)
        assert (
            data ==
            {
                'id': exemple.id,
                'url': "https://doc.anyblok.org",
            }
        )

    def test_url_with_a_valid_url(self, registry_field_url):
        registry = registry_field_url
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'url': "https://doc.anyblok.org",
        }
        load_data = exemple_schema.load(dump_data)
        assert dump_data == load_data

    def test_url_with_an_invalid_url(self, registry_field_url):
        registry = registry_field_url
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'url': 'anyblok'
        }
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(dump_data)

        assert (
            exception._excinfo[1].messages ==
            {'url': ['Not a valid URL.']}
        )


def add_field_phonenumber():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        phonenumber = PhoneNumber()


@pytest.fixture(scope="class")
def registry_field_phonenumber(request, bloks_loaded):
    registry = init_registry(add_field_phonenumber)
    request.addfinalizer(registry.close)
    return registry


@pytest.mark.skipif(not has_phonenumbers,
                    reason="phonenumbers is not installed")
class TestFieldPhonenumber:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_phonenumber):
        transaction = registry_field_phonenumber.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_phonenumber_field_type(self, registry_field_phonenumber):
        registry = registry_field_phonenumber
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        assert (
            isinstance(exemple_schema.schema.fields['phonenumber'],
                       fields.PhoneNumber))

    def test_dump_phonenumber(self, registry_field_phonenumber):
        registry = registry_field_phonenumber
        exemple = registry.Exemple.insert(phonenumber='+33953537297')
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        data = exemple_schema.dump(exemple)
        assert (
            data ==
            {
                'id': exemple.id,
                'phonenumber': "+33 9 53 53 72 97",
            }
        )

    def test_phonenumber_with_a_valid_phonenumber(
        self, registry_field_phonenumber
    ):
        registry = registry_field_phonenumber
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'phonenumber': "09 53 53 72 97",
        }
        load_data = exemple_schema.load(dump_data)
        pn = PN("+33953537297", None)
        assert load_data == {'id': 1, 'phonenumber': pn}

    def test_phonenumber_with_a_valid_phonenumber_and_other_region(
        self, registry_field_phonenumber
    ):
        registry = registry_field_phonenumber
        exemple_schema = SchemaWrapper(
            registry=registry,
            context={'model': "Model.Exemple", "region": "GB"})
        dump_data = {
            'id': 1,
            'phonenumber': "020 8366 1177",
        }
        load_data = exemple_schema.load(dump_data)
        pn = PN("+442083661177", None)
        assert load_data == {'id': 1, 'phonenumber': pn}

    def test_phonenumber_with_an_international_valid_phonenumber(
        self, registry_field_phonenumber
    ):
        registry = registry_field_phonenumber
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'phonenumber': "+33953537297",
        }
        load_data = exemple_schema.load(dump_data)
        pn = PN("+33953537297", None)
        assert load_data == {'id': 1, 'phonenumber': pn}

    def test_phonenumber_with_an_invalid_phonenumber(
        self, registry_field_phonenumber
    ):
        registry = registry_field_phonenumber
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'phonenumber': 'anyblok'
        }
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(dump_data)

        assert (
            exception._excinfo[1].messages ==
            {'phonenumber': [
                'The string supplied did not seem to be a phone number.']}
        )


def add_field_country():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        country = Country()


@pytest.fixture(scope="class")
def registry_field_country(request, bloks_loaded):
    registry = init_registry(add_field_country)
    request.addfinalizer(registry.close)
    return registry


@pytest.mark.skipif(not has_pycountry, reason="pycountry is not installed")
class TestFieldCountry:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_country):
        transaction = registry_field_country.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_country_field_type(self, registry_field_country):
        registry = registry_field_country
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        assert (
            isinstance(exemple_schema.schema.fields['country'], fields.Country))

    def test_dump_country(self, registry_field_country):
        registry = registry_field_country
        exemple = registry.Exemple.insert(
            country=pycountry.countries.get(alpha_2='FR'))
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        data = exemple_schema.dump(exemple)
        assert (
            data ==
            {
                'id': exemple.id,
                'country': "FRA",
            }
        )

    def test_country_with_a_valid_country(self, registry_field_country):
        registry = registry_field_country
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'country': "FRA",
        }
        load_data = exemple_schema.load(dump_data)
        assert (
            load_data ==
            {'id': 1, 'country': pycountry.countries.get(alpha_2='FR')}
        )

    def test_country_with_an_invalid_country(self, registry_field_country):
        registry = registry_field_country
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'country': 'ARF'
        }
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load(dump_data)

        assert (
            exception._excinfo[1].messages ==
            {'country': ['Not a valid country.']}
        )

    def test_country_alpha_2_mode(self):

        # Define some schema to test Country Field configuration
        class ExampleCountrySchema(Schema):
            country = fields.Country(mode=fields.Country.Modes.ALPHA_2)

        sch = ExampleCountrySchema()

        country = sch.load(dict(country='FR'))

        assert isinstance(
                country.get('country'), type(
                    pycountry.countries.get(alpha_3='FRA')))
        assert country.get('country') == pycountry.countries.get(
                alpha_3='FRA')

        country = sch.dump(country)

        assert isinstance(country, dict)
        assert country == {
                'country': 'FR'
                }

    def test_country_numeric_mode(self):

        # Define some schema to test Country Field configuration
        class ExampleCountrySchema(Schema):
            country = fields.Country(mode=fields.Country.Modes.NUMERIC)

        sch = ExampleCountrySchema()

        country = sch.load(dict(country='250'))

        assert isinstance(
                country.get('country'), type(
                    pycountry.countries.get(alpha_3='FRA')))
        assert country.get('country') == pycountry.countries.get(
                alpha_3='FRA')

        country = sch.dump(country)

        assert isinstance(country, dict)
        assert country == {
                'country': '250'
                }

    def test_country_name_mode(self):

        # Define some schema to test Country Field configuration
        class ExampleCountrySchema(Schema):
            country = fields.Country(mode=fields.Country.Modes.NAME)

        sch = ExampleCountrySchema()

        country = sch.load(dict(country='France'))

        assert isinstance(
                country.get('country'), type(
                    pycountry.countries.get(alpha_3='FRA')))
        assert country.get('country') == pycountry.countries.get(
                alpha_3='FRA')

        country = sch.dump(country)

        assert isinstance(country, dict)
        assert country == {
                'country': 'France'
                }

    def test_country_official_name_mode(self):

        # Define some schema to test Country Field configuration
        class ExampleCountrySchema(Schema):
            country = fields.Country(mode=fields.Country.Modes.OFFICIAL_NAME)

        sch = ExampleCountrySchema()

        country = sch.load(dict(country='French Republic'))

        assert isinstance(
                country.get('country'), type(
                    pycountry.countries.get(alpha_3='FRA')))
        assert country.get('country') == pycountry.countries.get(
                alpha_3='FRA')

        country = sch.dump(country)

        assert isinstance(country, dict)
        assert country == {
                'country': 'French Republic'
                }

    def test_country_unknown_mode(self):

        with pytest.raises(ValueError) as exception:
            # Define some schema to test Country Field configuration
            class ExampleCountrySchema(Schema):
                country = fields.Country(mode="not_a_valid_mode")

        assert str(
                list(
                    fields.Country.Modes.__members__.keys()
                    )
                ) in str(exception.value)

    def test_country_different_load_and_dump_mode(self):

        # Define some schema to test Country Field configuration
        class ExampleCountrySchema(Schema):
            country = fields.Country(
                    load_mode=fields.Country.Modes.ALPHA_3,
                    dump_mode=fields.Country.Modes.ALPHA_2
                    )

        sch = ExampleCountrySchema()

        country = sch.load(dict(country='FRA'))
        assert country.get('country') == pycountry.countries.get(alpha_3='FRA')

        country = sch.dump(country)
        assert country == {
                'country': 'FR'
                }


def add_field_color():

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        color = Color()


@pytest.fixture(scope="class")
def registry_field_color(request, bloks_loaded):
    registry = init_registry(add_field_color)
    request.addfinalizer(registry.close)
    return registry


@pytest.mark.skipif(not has_colour, reason="colour is not installed")
class TestFieldColor:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_field_color):
        transaction = registry_field_color.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_colour_field_type(self, registry_field_color):
        registry = registry_field_color
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        assert (
            isinstance(exemple_schema.schema.fields['color'], fields.Color))

    def test_dump_colour(self, registry_field_color):
        registry = registry_field_color
        exemple = registry.Exemple.insert(color=colour.Color('#F5F5F5'))
        assert exemple.color.hex == '#f5f5f5'
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        data = exemple_schema.dump(exemple)
        assert (
            data ==
            {
                'id': exemple.id,
                'color': "#f5f5f5",
            }
        )

    def test_colour_with_a_valid_color(self, registry_field_color):
        registry = registry_field_color
        exemple_schema = SchemaWrapper(
            registry=registry, context={'model': "Model.Exemple"})
        dump_data = {
            'id': 1,
            'color': "#F5F5F5",
        }
        load_data = exemple_schema.load(dump_data)
        assert (
            load_data ==
            {'id': 1, 'color': colour.Color('#F5F5F5')}
        )
