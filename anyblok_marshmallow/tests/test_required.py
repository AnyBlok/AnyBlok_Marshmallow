# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from . import ExempleSchema
from anyblok_marshmallow import SchemaWrapper


class TestRequired:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_simple_model):
        transaction = registry_simple_model.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_schema_with_required_in_meta(self, registry_simple_model):
        registry = registry_simple_model

        class MySchema(SchemaWrapper):
            model = 'Model.Exemple'
            required_fields = True

        exemple_schema = MySchema(registry=registry)
        fields = exemple_schema.schema.fields
        assert fields['id'].required
        assert fields['name'].required
        assert fields['number'].required

    def test_schema_with_required_list_in_meta(self, registry_simple_model):
        registry = registry_simple_model

        class MySchema(SchemaWrapper):
            model = 'Model.Exemple'
            required_fields = ['name', 'number']

        exemple_schema = MySchema(registry=registry)
        fields = exemple_schema.schema.fields
        assert not fields['id'].required
        assert fields['name'].required
        assert fields['number'].required

    def test_schema_with_required_in_context(self, registry_simple_model):
        registry = registry_simple_model
        exemple_schema = ExempleSchema(
            context={'registry': registry, 'required_fields': True})
        fields = exemple_schema.schema.fields
        assert fields['id'].required
        assert fields['name'].required
        assert fields['number'].required

    def test_schema_with_required_list_in_context(self, registry_simple_model):
        registry = registry_simple_model
        exemple_schema = ExempleSchema(
            context={'registry': registry,
                     'required_fields': ['name', 'number']})
        fields = exemple_schema.schema.fields
        assert not fields['id'].required
        assert fields['name'].required
        assert fields['number'].required

    def test_schema_with_required_in_validate(self, registry_simple_model):
        registry = registry_simple_model
        exemple_schema = ExempleSchema(context={'registry': registry})
        assert (
            exemple_schema.validate({'id': 1, 'name': 'test'},
                                    required_fields=True) ==
            {'number': ['Missing data for required field.']}
        )

    def test_schema_with_required_list_in_validate(self, registry_simple_model):
        registry = registry_simple_model
        exemple_schema = ExempleSchema(context={'registry': registry})
        assert (
            exemple_schema.validate({'id': 1, 'name': 'test'},
                                    required_fields=['name', 'number']) ==
            {'number': ['Missing data for required field.']}
        )
