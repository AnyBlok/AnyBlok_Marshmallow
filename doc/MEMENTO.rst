.. This file is a part of the AnyBlok / Marshmallow project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

Memento
=======

Declare your **AnyBlok model**
------------------------------

::

    from anyblok.column import Integer, String
    from anyblok.relationship import Many2One, Many2Many
    from anyblok import Declarations


    @Declarations.register(Declarations.Model)
    class City:

        id = Integer(primary_key=True)
        name = String(nullable=False)
        zipcode = String(nullable=False)

        def __repr__(self):
            return '<City(name={self.name!r})>'.format(self=self)


    @Declarations.register(Declarations.Model)
    class Tag:

        id = Integer(primary_key=True)
        name = String(nullable=False)

        def __repr__(self):
            return '<Tag(name={self.name!r})>'.format(self=self)


    @Declarations.register(Declarations.Model)
    class Customer:
        id = Integer(primary_key=True)
        name = String(nullable=False)
        tags = Many2Many(model=Declarations.Model.Tag)

        def __repr__(self):
            return '<Customer(name={self.name!r}, '
                   'tags={self.tags!r})>'.format(self=self)


    @Declarations.register(Declarations.Model)
    class Address:

        id = Integer(primary_key=True)
        street = String(nullable=False)
        city = Many2One(model=Declarations.Model.City, nullable=False)
        customer = Many2One(
            model=Declarations.Model.Customer, nullable=False,
            one2many="addresses")


.. warning::

    The **AnyBlok model** must be declared in a blok


Declare your schema
-------------------

::

    from anyblok_marshmallow import SchemaWrapper, PostLoadSchema, Nested

    class CitySchema(SchemaWrapper):
        model = 'Model.City'


    class TagSchema(SchemaWrapper):
        model = 'Model.Tag'


    class AddressSchema(SchemaWrapper):
        model = 'Model.Address'

        class Schema:
            # Add some marshmallow fields or behaviours

            # follow the relationship Many2One and One2One
            city = Nested(CitySchema)


    class CustomerSchema(SchemaWrapper):
        model = 'Model.Customer'
        # optionally attach an AnyBlok registry
        # to use for serialization, desarialization and validation
        registry = registry

        class Schema(PostLoadSchema):
            # follow the relationship One2Many and Many2Many
            # - the many=True is required because it is *2Many
            # - exclude is used to forbid the recurse loop
            addresses = Nested(AddressSchema, many=True, exclude=('customer', ))
            tags = Nested(TagSchema, many=True)


    customer_schema = CustomerSchema()


.. note::

    **New** in version **1.1.0** the Nested field must come from **anyblok_marshmallow**,
    because **marshmallow** cache the Nested field with the context. And the context is not propagated
    again if it changed

.. note::

    **Ref** in version **1.4.0**, ``post_load_return_instance`` was replaced by the mixin class
    ``PostLoadSchema``

.. note::

    **Ref** in version **2.1.0**, ``ModelSchema`` was replaced by ``SchemaWrapper``. This action
    break the compatibility with the previous version, but allow to follow the upgrade of **marshmallow**


(De)serialize your data and validate it
---------------------------------------

::

    customer = registry.Customer.insert(name="JS Suzanne")
    tag1 = registry.Tag.insert(name="tag 1")
    customer.tags.append(tag1)
    tag2 = registry.Tag.insert(name="tag 2")
    customer.tags.append(tag2)
    rouen = registry.City.insert(name="Rouen", zipcode="76000")
    paris = registry.City.insert(name="Paris", zipcode="75000")
    registry.Address.insert(customer=customer, street="Somewhere", city=rouen)
    registry.Address.insert(customer=customer, street="Another place", city=paris)

    dump_data = customer_schema.dump(customer).data
    # {
    #     'id': 1,
    #     'name': 'JS Suzanne',
    #     'tags': [
    #         {
    #             'id': 1,
    #             'name': 'tag 1',
    #         },
    #         {
    #             'id': 2,
    #             'name': 'tag 2',
    #         },
    #     ],
    #     'addresses': [
    #         {
    #             'id': 1
    #             'street': 'Somewhere'
    #             'city': {
    #                 'id': 1,
    #                 'name': 'Rouen',
    #                 'zipcode': '76000',
    #             },
    #         },
    #         {
    #             'id': 2
    #             'street': 'Another place'
    #             'city': {
    #                 'id': 2,
    #                 'name': 'Paris',
    #                 'zipcode': '75000',
    #             },
    #         },
    #     ],
    # }

    customer_schema.load(dump_data).data
    # <Customer(name='JS Suzanne' tags=[<Tag(name='tag 1')>, <Tag (name='tag 2')>])>

    errors = customer_schema.validate(dump_data)
    # dict with all the validating errors

.. note::

    We have an instance of the model cause of the mixin ``PostLoadSchema``


Give the registry
-----------------

The schema need to have the registry.

If no registry found when the de(serialization) or validation then the 
**RegistryNotFound** exception will be raised.

Add the **registry** by the class attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the solution given in the main exemple::

    class CustomerSchema(SchemaWrapper):
        model = 'Model.Customer'
        registry = registry


Add the **registry** during init
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This solution is use during the instanciation

::

    customer_schema = CustomerSchema(registry=registry)


Add the **registry** by the context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This solution is use during the instanciation or after

::

    customer_schema = CustomerSchema(context={'registry': registry})

or

::

    customer_schema = CustomerSchema()
    customer_schema.context['registry'] = registry


Add the **registry** when the de(serialization or validator is called
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    customer_schema.dumps(customer, registry=registry)
    customer_schema.dump(customer, registry=registry)
    customer_schema.loads(dump_data, registry=registry)
    customer_schema.load(dump_data, registry=registry)
    customer_schema.validate(dump_data, registry=registry)


**model** option
----------------

This option add in the model name. As the registry, this option
can be passed by definition, initialization, context or during the call of the (de)serialization / validation

::

    class AnySchema(SchemaWrapper):
        model = "Model.Customer"

or

::

    any_schema = AnySchema(model="Model.customer")

or

::

    any_schema.context['model'] = "Model.Customer"

or

::

    any_schema.dumps(instance, model="Model.Customer")
    any_schema.dump(instance, model="Model.Customer")
    any_schema.loads(dump_data, model="Model.Customer")
    any_schema.load(dump_data, model="Model.Customer")
    any_schema.validate(dump_data, model="Model.Customer")


**only_primary_key** option
---------------------------

This option add in the only argument the primary keys of the model. As the registry, this option
can be passed by definition, initialization, context or during the call of the (de)serialization / validation

::

    class CustomerSchema(SchemaWrapper):
        model = "Model.Customer"
        only_primary_key = True

or

::

    customer_schema = CustomerSchema(only_primary_key=True)

or

::

    customer_schema.context['only_primary_key'] = True

or

::

    customer_schema.dumps(instance, only_primary_key=True)
    customer_schema.dump(instance, only_primary_key=True)
    customer_schema.loads(dump_data, only_primary_key=True)
    customer_schema.load(dump_data, only_primary_key=True)
    customer_schema.validate(dump_data, only_primary_key=True)


**required_fields** option
--------------------------

This option force the generated fields, and only them to be requried.

::

    class CustomerSchema(SchemaWrapper):
        model = "Model.Customer"
        required_fields = True
        # or required_fields = [ list of fieldname ]

or

::

    customer_schema = CustomerSchema(required_fields=True)

or

::

    customer_schema.context['required_fields'] = True

or

::

    customer_schema.loads(dump_data, required_fields=True)
    customer_schema.load(dump_data, required_fields=True)
    customer_schema.validate(dump_data, required_fields=True)

.. note:: All the attributes can take **True** or the list of the fieldname to be required

Use the field JsonCollection
----------------------------

This field allow the schema to inspect an AnyBlok.fields.Json in an any specific instance to 
validate the value.

AnyBlok models::

    @register(Model)
    class Template:
        name = anyblok.column.String(primary_key=True)
        properties = anyblok.column.Json(defaumt={})

    @register(Model)
    class SaleOrder:
        id = anyblok.column.Integer(primary_key=True)
        number = anyblok.column.Integer(nullable=False)
        discount = anyblok.column.Integer()

AnyBlok / Marchmallow schema::

    class SaleOrderSchema(SchemaWrapper):
        model = 'Model.SaleOrder'

        class Schema:
            discount = JsonCollection(
                fieldname='properties',
                keys=['allowed_discount'],
                cls_or_instance_type=marshmallow.fields.Integer(required=True)
            )

Use::

    goodcustomer = registry.Template.insert(
        name='Good customer',
        properties={'allowed_discount': [10, 15, 30]
    )
    customer = registry.Template.insert(
        name='Customer',
        properties={'allowed_discount': [0, 5, 10]
    )
    badcustomer = registry.Template.insert(
        name='Bad customer',
        properties={'allowed_discount': [0]
    )

    schema = SaleOrderSchema(registry=registry)

    --------------------------

    data = schema.load(
        {
            number='SO0001',
            discount=10,
        },
        instances={'default': goodcustomer}
    )

    --------------------------

    data = schema.load(
        {
            number='SO0001',
            discount=10,
        },
        instances={'default': customer}
    )
    ==> error = {}

    --------------------------

    data = schema.load(
        {
            number='SO0001',
            discount=10,
        },
        instances={'default': badcustomer}
    )
    ==> error = {'discount': ['Not a valid choice']}
