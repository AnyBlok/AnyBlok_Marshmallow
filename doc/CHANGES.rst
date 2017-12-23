.. This file is a part of the AnyBlok / Marshmallow project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

CHANGELOG
=========

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
