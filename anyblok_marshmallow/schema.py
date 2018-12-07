# This file is a part of the AnyBlok / Marshmallow api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from marshmallow import post_load, validates_schema, validate
from marshmallow_sqlalchemy.schema import (
    ModelSchema as MS,
    ModelSchemaOpts as MSO
)
from marshmallow_sqlalchemy.convert import ModelConverter as MC
from anyblok.common import anyblok_column_prefix
from marshmallow.exceptions import ValidationError
from .exceptions import RegistryNotFound
from .fields import (
    Raw, Nested, Text, Email, URL, PhoneNumber, Country, String, DateTime,
    Color, UUID, Float, Boolean, Integer, Time, Date, TimeDelta, Decimal
)
import anyblok
import sqlalchemy as sa
import sqlalchemy_utils.types as sau
from marshmallow.base import SchemaABC
from marshmallow.compat import binary_type, text_type
import datetime as dt
import uuid
import decimal


def update_from_kwargs(*entries):
    """decorator to get temporaly the value in kwargs and put it in schema

    :params entries: array ok entry name to take from the kwargs
    """

    def wrap_function(f):

        def wrap_call(*args, **kwargs):
            instance = args[0]
            old_vals = []
            for entry in entries:
                if hasattr(instance, entry):
                    old_vals.append((entry, getattr(instance, entry)))

                if entry in kwargs:
                    setattr(instance, entry, kwargs.pop(entry))

            try:
                return f(*args, **kwargs)
            finally:
                for entry, value in old_vals:
                    setattr(instance, entry, value)

        return wrap_call

    return wrap_function


def format_fields(x):
    """remove the anyblok prefix form the field name"""
    if x.startswith(anyblok_column_prefix):
        return x[len(anyblok_column_prefix):]

    return x


class ModelConverter(MC):
    """Overwrite the ModelConverter class of marshmallow-sqlalchemy

    The goal if to fix the fieldname, because they are prefixed.
    """
    SQLA_TYPE_MAPPING = MC.SQLA_TYPE_MAPPING.copy()
    SQLA_TYPE_MAPPING.update({
        sa.Text: Text,
        sau.email.EmailType: Email,
        sau.url.URLType: URL,
        sau.phone_number.PhoneNumberType: PhoneNumber,
        sau.encrypted.encrypted_type.EncryptedType: String,
        sau.uuid.UUIDType: UUID,
        sau.color.ColorType: Color,
        anyblok.column.CountryType: Country,
        anyblok.column.StringType: String,
        anyblok.column.SelectionType: String,
        anyblok.column.DateTimeType: DateTime,
        anyblok.column.TextType: Text,
    })

    def fields_for_model(self, Model, **kwargs):
        """Overwrite the method and remove prefix of the field name"""
        res = super(ModelConverter, self).fields_for_model(Model, **kwargs)
        for field in Model.loaded_fields.keys():
            res[field] = Raw()

        fields = {format_fields(x): y for x, y in res.items()}
        fields_description = Model.fields_description()
        for field in fields:
            if field not in fields_description:
                continue

            type_ = fields_description[field]['type']
            if type_ == 'Selection':
                validators = fields[field].validate
                choices = list(dict(
                    fields_description[field]['selections']).keys())
                labels = list(dict(
                    fields_description[field]['selections']).values())
                validators.append(validate.OneOf(choices, labels=labels))
            elif type_ in ('Many2One', 'One2One', 'One2Many', 'Many2Many'):
                many = False if type_ in ('Many2One', 'One2One') else True
                remote_model = fields_description[field]['model']
                RemoteModel = Model.registry.get(remote_model)

                sch = type(
                    'Model.Schema.' + remote_model,
                    (SchemaWrapper,),
                    {'model': remote_model}
                )

                fields[field] = Nested(
                    sch, many=many, only=RemoteModel.get_primary_keys())

        return fields

    def _add_column_kwargs(self, kwargs, column):
        super(ModelConverter, self)._add_column_kwargs(kwargs, column)
        required_fields = self.schema_cls.Meta.required_fields
        if (
            (isinstance(required_fields, (tuple, list)) and
             column.name in required_fields) or
            required_fields is True
        ):
            kwargs['required'] = True
            kwargs['allow_none'] = False

        if isinstance(column.type, sau.phone_number.PhoneNumberType):
            kwargs['region'] = column.type.region
        elif isinstance(column.type, anyblok.column.CountryType):
            import pycountry
            choices = [x.alpha_3 for x in pycountry.countries]
            labels = [x.name for x in pycountry.countries]
            validators = kwargs.get('validate', [])
            validators.append(validate.OneOf(choices, labels=labels))


class TemplateSchema:
    """Base class of Schema generated by ``SchemaWrapper``"""
    OPTIONS_CLASS = MSO

    @validates_schema(pass_original=True, skip_on_field_errors=False)
    def check_unknown_fields(self, data, original_data):
        od = set(original_data.keys())
        unknown = od - set(self.fields)
        if unknown:
            raise ValidationError(
                'Unknown fields %r on Model %s' % (
                    unknown, self.opts.model.__registry_name__
                ),
                unknown.pop()
            )

    @post_load
    def make_instance(self, data):
        return self.get_instance_from(data)

    def get_instance_from(self, data):
        try:
            return super(TemplateSchema, self).get_instance_from(data)
        except ValidationError:
            raise
        except Exception:
            return data


class PostLoadSchema:
    """Return the AnyBlok instance from marshmallow deserialize"""
    post_load_attributes = True

    def valid_postload(self, postload, data, fields):
        if not postload:
            raise ValidationError(
                {
                    "instance": (
                        "No instance of %r found with the filter keys "
                        "%r" % (self.opts.model, fields)
                    ),
                },
                fields_name=["instance"],
                data=data
            )
        elif isinstance(postload, list):
            if len(postload) > 1:
                raise ValidationError(
                    {
                        "instance": (
                            "%s instances of %r found with the filter "
                            "keys %r" % (
                                len(postload), self.opts.model, fields)
                        ),
                    },
                    fields_name=["instance"],
                    data=data
                )
            else:
                postload = postload[0]

        return postload

    def get_instance_from(self, data):
        if self.post_load_attributes is True:
            Model = self.opts.model
            pks = Model.get_primary_keys()
            _pks = {x: data[x] for x in pks}
            return self.valid_postload(
                Model.from_primary_keys(**_pks), data, pks)

        if isinstance(self.post_load_attributes, list):
            Model = self.opts.model
            query = Model.query()
            filter_by = {}
            for field in self.post_load_attributes:
                if field not in data:
                    raise ValidationError(
                        {
                            "KeyError": "%r is unknow in the data" % field,
                        },
                        fields_name=[field],
                        data=data
                    )

                filter_by[field] = data[field]

            query = query.filter_by(**filter_by)
            return self.valid_postload(
                query.all(), data, self.post_load_attributes)

        return data


class SchemaWrapper(SchemaABC):
    """Schema Wrapper to generate marshmallow schema

    ::

        class MySchema(SchemaWrapper):
            model = 'Model.Name'


    the wrapper implement the **marshmallow.base.SchemaABC** abstract
    class. And call the methods of the marshmallow schema with the same
    parameter

    Some class attributes can be added to improve the schema:

    * **model**: str, the registry name of the AnyBlok model
    * **required_fields**: list of the field which become required
      In this case the anyblok columns are not required but schema
      force them to be required
    * registry: the anyblok registry, only if you know it
    * only_primary_key: boolean, if True the marshmallow parameter only
      will be filled with the name of the primary keys.

    .. note::

        The model and registry are required to generate the schema. they can be
        defined by class attribute, parameter in the methods (load, loads,
        validate, dump, dumps) or in the context attribute.
    """

    model = None
    required_fields = None
    registry = None
    only_primary_key = None

    class Schema:
        pass

    def __init__(self, *args, **kwargs):
        self.registry = kwargs.pop('registry', self.registry)
        self.context = kwargs.pop('context', {})
        self.only_primary_key = kwargs.pop(
            'only_primary_key', self.only_primary_key)
        self.model = kwargs.pop('model', self.model)

        self.required_fields = kwargs.pop(
            'required_fields', self.required_fields)
        self.instances = kwargs.pop('instances', {})
        self.args = args
        self.kwargs = kwargs

    def generate_marsmallow_instance(self):
        """Generate the real mashmallow-sqlalchemy schema"""
        registry = self.context.get('registry', self.registry)
        required_fields = self.context.get(
            'required_fields', self.required_fields)
        model = self.context.get('model', self.model)
        only_primary_key = self.context.get(
            'only_primary_key', self.only_primary_key)

        cls_name = 'Model.Schema.%s' % model
        if registry is None:
            raise RegistryNotFound(
                'No registry found for create schema %r' % cls_name)

        Schema = type(
            cls_name, (TemplateSchema, self.Schema, MS),
            {
                'Meta': type(
                    'Meta',
                    tuple(),
                    {
                        'model': registry.get(model),
                        'sqla_session': registry.Session,
                        'model_converter': ModelConverter,
                        'required_fields': required_fields,
                    },
                ),
                'TYPE_MAPPING': {
                    text_type: String,
                    binary_type: String,
                    dt.datetime: DateTime,
                    float: Float,
                    bool: Boolean,
                    tuple: Raw,
                    list: Raw,
                    set: Raw,
                    int: Integer,
                    uuid.UUID: UUID,
                    dt.time: Time,
                    dt.date: Date,
                    dt.timedelta: TimeDelta,
                    decimal.Decimal: Decimal,
                }
            }
        )

        kwargs = self.kwargs.copy()

        if only_primary_key:
            Model = registry.get(model)
            pks = Model.get_primary_keys()
            kwargs['only'] = pks

        schema = Schema(*self.args, **kwargs)
        schema.context.update(self.context)
        schema.context['registry'] = registry
        schema.context['instances'] = self.instances

        return schema

    @property
    def schema(self):
        """property to get the real schema"""
        return self.generate_marsmallow_instance()

    @update_from_kwargs('registry', 'only_primary_key', 'model', 'instances',
                        'required_fields')
    def loads(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.loads(*args, **kwargs)

    @update_from_kwargs('registry', 'only_primary_key', 'model', 'instances',
                        'required_fields')
    def load(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.load(*args, **kwargs)

    @update_from_kwargs('registry', 'only_primary_key', 'model', 'instances')
    def dumps(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.dumps(*args, **kwargs)

    @update_from_kwargs('registry', 'only_primary_key', 'model', 'instances')
    def dump(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.dump(*args, **kwargs)

    @update_from_kwargs('registry', 'only_primary_key', 'model', 'instances',
                        'required_fields')
    def validate(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.validate(*args, **kwargs)

    def _update_fields(self, *args, **kwargs):
        return self.schema._update_fields(*args, **kwargs)
