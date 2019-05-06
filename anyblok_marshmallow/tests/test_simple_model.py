# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from . import ExempleSchema
from marshmallow.exceptions import ValidationError


class TestSimpleModel:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_simple_model):
        transaction = registry_simple_model.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_dump_simple_schema(self, registry_simple_model):
        registry = registry_simple_model
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data = exemple_schema.dump(exemple)
        assert data == {'number': None, 'id': 1, 'name': 'test'}

    def test_load_simple_schema_1(self, registry_simple_model):
        registry = registry_simple_model
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data = exemple_schema.load({'id': exemple.id, 'name': exemple.name})
        assert data == {'id': exemple.id, 'name': exemple.name}

    def test_load_simple_schema_2(self, registry_simple_model):
        registry = registry_simple_model
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load({'id': exemple.id})

        assert (
            exception._excinfo[1].messages ==
            {'name': ["Missing data for required field."]}
        )

    def test_load_simple_schema_3(self, registry_simple_model):
        registry = registry_simple_model
        exemple_schema = ExempleSchema(
            partial=('name',), context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data = exemple_schema.load({'id': exemple.id})
        assert data == {'id': exemple.id}

    def test_load_simple_schema_4(self, registry_simple_model):
        registry = registry_simple_model
        exemple_schema = ExempleSchema(
            partial=('name',), context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        with pytest.raises(ValidationError) as exception:
            exemple_schema.load({'id': exemple.id, 'name': None})

        assert (
            exception._excinfo[1].messages ==
            {'name': ['Field may not be null.']}
        )

    def test_validate_simple_schema(self, registry_simple_model):
        registry = registry_simple_model
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        errors = exemple_schema.validate(
            {'id': exemple.id, 'name': exemple.name, 'number': 'test'})
        assert errors == {'number': ['Not a valid integer.']}
