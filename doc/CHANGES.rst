.. This file is a part of the AnyBlok / Marshmallow project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

CHANGELOG
=========

2.2.0 (2018-10-17)
------------------

* Fixed the convertion of type between **AnyBlok.Column** and **marshmallow.Field**

2.1.0 (2018-09-26)
------------------

* Fixed the compatibility with **Marshmallow > 3.0.0b8**
* Removed ``ModelSchema`` class
* Added ``SchemaWrapper``, this is the best way to defined a generated
  schema with the **marshmallow_sqlalchemy** library

.. warning::

    This version break the compatibility with previous version, in the only
    goal to be adapted with the latest version of **marshmallow**

2.0.1 (2018-06-07)
------------------

* Fix required_field put allow_none to False

2.0.0 (2018-05-30)
------------------

* Add JsonCollection field, Allow to add a check in function of an collection
  stored in a AnyBlok.fields.Json
* Add Text field, to represent an ``anyblok.column.Text``
* Migration of the code and unit test to marshmallow 3.0.0
* Add Email matching for ``anyblok.column.Email``
* Add URL matching for ``anyblok.column.URL``
* Add PhoneNumber matching for ``anyblok.column.PhoneNumber``
* Add Country matching for ``anyblok.column.Country``
* Add required_fields option
* Add InstanceField

1.4.0 (2018-04-07)
------------------

* Replace **post_load_return_instance** method by **PostLoadSchema** class
* In the case of the field **Selection**, the validator **OneOf** is 
  applied with the available values come from the AnyBlok columns
* Replace **marshmallow_sqlalchemy.fields.Related** by 
  **anyblok_marshmallow.fields.Nested**. The goal is to improve the consistent 
  between all field in the schema

1.3.0 (2017-12-23)
------------------

* [ADD] unittest on some case
* [FIX] AnyBlok field.Function is return as MarshMallow fields.Raw
* [ADD] fields.File, type to encode and decode to/from base 64

1.2.0 (2017-11-30)
------------------

* [REF] decrease complexity
* [IMP] Add ``validates_schema`` on ModelSchema to automaticly check
  if the field exist on the model

1.1.0 (2017-11-02)
------------------

* Add option put only the primary keys
* Fix the Front page
* REF model option, can be given by another way than Meta
* Put RegistryNotFound in exceptions
* Add Nested field, this field is not and have not to be cached

1.0.2 (2017-10-25)
------------------

* Fix pypi documentation

1.0.0 (2017-10-24)
------------------

* Add marshmallow schema for AnyBlok for:

  - Serialization
  - Deserialization
  - Validation
