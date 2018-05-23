# This file is a part of the AnyBlok / Marshmallow api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from marshmallow import (
    Schema, post_load, SchemaOpts, validates_schema, validate
)
from marshmallow_sqlalchemy.schema import (
    ModelSchema as MS,
    ModelSchemaOpts as MSO
)
from marshmallow_sqlalchemy.convert import ModelConverter as MC
from anyblok.common import anyblok_column_prefix
from marshmallow.exceptions import ValidationError
from .exceptions import RegistryNotFound
from .fields import Raw, Nested, Text, Email, URL, PhoneNumber, Country
import anyblok
import sqlalchemy as sa
import sqlalchemy_utils.types as sau


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
        anyblok.column.CountryType: Country
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
                    (ModelSchema,),
                    {'Meta': type('Meta', tuple(), {'model': remote_model})}
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

        if isinstance(column.type, sau.phone_number.PhoneNumberType):
            kwargs['region'] = column.type.region
        elif isinstance(column.type, anyblok.column.CountryType):
            import pycountry
            choices = [x.alpha_3 for x in pycountry.countries]
            labels = [x.name for x in pycountry.countries]
            validators = kwargs.get('validate', [])
            validators.append(validate.OneOf(choices, labels=labels))


class ModelSchemaOpts(SchemaOpts):
    """Model schema option for Model schema

    Add get option from the Meta:

    * model: name of an AnyBlok model **required**
    * registry: an AnyBlok registry
    """
    def __init__(self, meta, *args, **kwargs):
        super(ModelSchemaOpts, self).__init__(meta, *args, **kwargs)
        self.model = getattr(meta, 'model', False)
        self.registry = getattr(meta, 'registry', False)
        self.only_primary_key = getattr(meta, 'only_primary_key', False)
        self.required_fields = getattr(meta, 'required_fields', None)


class TemplateSchema:
    OPTIONS_CLASS = MSO
    __init__ = MS.__init__
    load = MS.load
    dump = MS.dump
    validate = MS.validate

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        od = set(original_data.keys())
        unknown = od - set(self.fields)
        if unknown:
            raise ValidationError(
                'Unknown fields %r on Model %s' % (
                    unknown, self.opts.model.__registry_name__
                ),
                unknown
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


class ModelSchema(Schema):
    """A marshmallow schema based on the AnyBlok Model

    Wrap the real schema, because at the instanciation
    the registry is not available
    """
    OPTIONS_CLASS = ModelSchemaOpts

    def __init__(self, *args, **kwargs):
        registry = kwargs.pop('registry', None)
        only_primary_key = kwargs.pop('only_primary_key', None)
        model = kwargs.pop('model', None)
        required_fields = kwargs.pop('required_fields', None)
        self.instances = kwargs.pop('instances', {})
        super(ModelSchema, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.registry = registry or self.opts.registry
        self.model = model or self.opts.model
        self.required_fields = required_fields or self.opts.required_fields
        self.only_primary_key = only_primary_key or self.opts.only_primary_key

    def get_registry(self):
        registry = self.context.get('registry', self.registry)
        if not registry:
            raise RegistryNotFound(
                'No registry found to build schema %r' % self)

        return registry

    def get_only_primary_key(self):
        return self.context.get('only_primary_key', self.only_primary_key)

    def get_model(self):
        return self.context.get('model', self.model)

    def get_required_fields(self):
        return self.context.get('required_fields', self.required_fields)

    def generate_marsmallow_instance(self):
        """Generate the real mashmallow-sqlalchemy schema"""
        model = self.get_model()
        registry = self.get_registry()
        instances = self.context.get('instances', self.instances)
        only_primary_key = self.get_only_primary_key()
        required_fields = self.get_required_fields()

        Schema = type(
            'Model.Schema.%s' % model,
            (TemplateSchema, self.__class__, MS),
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
            }
        )

        kwargs = self.kwargs.copy()

        if only_primary_key:
            Model = registry.get(model)
            pks = Model.get_primary_keys()
            kwargs['only'] = pks

        schema = Schema(*self.args, **kwargs)
        schema.context['registry'] = registry
        schema.context['instances'] = instances

        return schema

    @property
    def schema(self):
        """property to get the real schema"""
        return self.generate_marsmallow_instance()

    @update_from_kwargs('registry', 'only_primary_key', 'model', 'instances',
                        'required_fields')
    def load(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.load(*args, **kwargs)

    @update_from_kwargs('registry', 'only_primary_key', 'model', 'instances')
    def dump(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.dump(*args, **kwargs)

    @update_from_kwargs('registry', 'only_primary_key', 'model', 'instances',
                        'required_fields')
    def validate(self, *args, **kwargs):
        """overload the main method to call in it in the real schema"""
        return self.schema.validate(*args, **kwargs)
