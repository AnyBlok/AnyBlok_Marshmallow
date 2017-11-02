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

    from anyblok_marshmallow import ModelSchema
    from anyblok_marshmallow.fields import Nested

    class CitySchema(ModelSchema):

        class Meta:
            model = 'Model.City'


    class TagSchema(ModelSchema):

        class Meta:
            model = 'Model.Tag'


    class AddressSchema(ModelSchema):

        # follow the relationship Many2One and One2One
        city = Nested(CitySchema)

        class Meta:
            model = 'Model.Address'


    class CustomerSchema(ModelSchema):

        # follow the relationship One2Many and Many2Many
        # - the many=True is required because it is *2Many
        # - exclude is used to forbid the recurse loop
        addresses = Nested(AddressSchema, many=True, exclude=('customer', ))
        tags = Nested(TagSchema, many=True)

        class Meta:
            model = 'Model.Customer'
            # optionally attach an AnyBlok registry
            # to use for serialization, desarialization and validation
            registry = registry
            # optionally return an AnyBlok model instance
            post_load_return_instance = True


    customer_schema = CustomerSchema()


.. note::

    **New** in version **1.1.0** the Nested field must come from **anyblok_marshmallow**,
    because **marshmallow** cache the Nested field with the context. And the context is not propagated
    again if it changed


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

    By default: the deserialization return a dict with deserialized data, 
    here we get an instance of the model because the ``CustomerSchema`` add 
    ``post_load_return_instance = True`` in their Meta


Give the registry
-----------------

The schema need to have the registry.

If no registry found when the de(serialization) or validation then the 
**RegistryNotFound** exception will be raised.

Add the **registry** by the Meta
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the solution given in the main exemple::

    class CustomerSchema(ModelSchema):

        class Meta:
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


Add the **registry** when the de(serialization or validatoris called
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    customer_schema.dump(customer, registry=registry)
    customer_schema.load(dump_data, registry=registry)
    customer_schema.validate(dump_data, registry=registry)


**post_load_return_instance** option
------------------------------------

As the registry this option can be passed by initialization of the schema, by the
context or during the call of methods

The value of this options can be:

* False: **default**, the output is a dict
* True: the output is an instance of the model. The primary keys must be in value
* array of string: the output is an instance of the model, each str entry must be an existing column

.. warning::

    If the option is not False, and the instance can no be found, then the **instance** error will be added
    in the errors dict of the method

.. warning::

    The post load is only for load method!!!


**model** option
----------------

This option add in the model name. As the registry, this option
can be passed by definition, initialization, context or during the call of the (de)serialization / validation

::

    class AnySchema(ModelSchema):

        class Meta:
            model = "Model.Customer"

or

::

    any_schema = AnySchema(model="Model.customer")

or

::

    any_schema.context['model'] = "Model.Customer"

or

::

    any_schema.dump(instance, model="Model.Customer")
    any_schema.load(dump_data, model="Model.Customer")
    any_schema.validate(dump_data, model="Model.Customer")


**only_primary_key** option
---------------------------

This option add in the only argument the primary keys of the model. As the registry, this option
can be passed by definition, initialization, context or during the call of the (de)serialization / validation

::

    class CustomerSchema(ModelSchema):

        class Meta:
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

    customer_schema.dump(instance, only_primary_key=True)
    customer_schema.load(dump_data, only_primary_key=True)
    customer_schema.validate(dump_data, only_primary_key=True)
