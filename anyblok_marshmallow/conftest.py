# This file is a part of the AnyBlok / Marshmallow project
#
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest  # noqa
from anyblok.conftest import *  # noqa


# -- wainting release 1.0.0 of anyblok --
from anyblok.testing import load_configuration


@pytest.fixture(scope='session')
def configuration_loaded(request):
    load_configuration()
