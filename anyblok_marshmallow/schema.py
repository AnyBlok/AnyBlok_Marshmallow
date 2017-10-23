# This file is a part of the AnyBlok / Marshmallow api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from marshmallow import Schema, post_load, SchemaOpts
from marshmallow_sqlalchemy.schema import (
    ModelSchema as MS,
    ModelSchemaOpts as MSO
)
from marshmallow_sqlalchemy.convert import ModelConverter as MC
from anyblok.common import anyblok_column_prefix


def format_fields(x):
    """remove the anyblok prefix form the field name"""
    if x.startswith(anyblok_column_prefix):
        return x[len(anyblok_column_prefix):]

    return x


class ModelConverter(MC):
    """Overwrite the ModelConverter class of marshmallow-sqlalchemy

    The goal if to fix the fieldname, because they are prefixed.
    """

    def fields_for_model(self, *args, **kwargs):
        """Overwrite the method and remove prefix of the field name"""
        res = super(ModelConverter, self).fields_for_model(*args, **kwargs)
        return {format_fields(x): y for x, y in res.items()}


class ModelSchemaOpts(SchemaOpts):
    """Model schema option for Model schema

    Add get option from the Meta:

    * model: name of an AnyBlok model **required**
    * registry: an AnyBlok registry
    * post_load_return_instance: return an instance object
    """
    def __init__(self, meta, *args, **kwargs):
        super(ModelSchemaOpts, self).__init__(meta, *args, **kwargs)
        self.model = getattr(meta, 'model', False)
        self.registry = getattr(meta, 'registry', False)
        self.post_load_return_instance = getattr(
            meta, 'post_load_return_instance', False)


class ModelSchema(Schema):
    """A marshmallow schema based on the AnyBlok Model

    Wrap the real schema, because at the instanciation
    the registry is not available
    """
    OPTIONS_CLASS = ModelSchemaOpts

    def __init__(self, *args, **kwargs):
        registry = kwargs.pop('registry', None)
        post_load_return_instance = kwargs.pop(
            'post_load_return_instance', None)
        super(ModelSchema, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self._schema = None
        self.registry = registry or self.opts.registry
        self.post_load_return_instance = (
            post_load_return_instance or self.opts.post_load_return_instance)

    def generate_marsmallow_instance(self):
        """Generate the real mashmallow-sqlalchemy schema"""
        registry = self.context.get('registry', self.registry)
        post_load_return_instance = self.context.get(
            'post_load_return_instance',
            self.post_load_return_instance)

        class Schema(self.__class__, MS):
            OPTIONS_CLASS = MSO

            __init__ = MS.__init__
            load = MS.load
            dump = MS.dump
            validate = MS.validate

            class Meta:
                model = registry.get(self.opts.model)
                sqla_session = registry.Session
                model_converter = ModelConverter

            @post_load
            def make_instance(self, data):
                return data

        self._schema = Schema(*self.args, **self.kwargs)
        self._schema.context['registry'] = registry
        self._schema.context['post_load_return_instance'] = (
            post_load_return_instance)
        return self._schema

    @property
    def schema(self):
        """property to get the real schema"""
        if not self._schema:
            return self.generate_marsmallow_instance()

        return self._schema

    def load(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.load(*args, **kwargs)

    def dump(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.dump(*args, **kwargs)

    def validate(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.validate(*args, **kwargs)
