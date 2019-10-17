# This file is a part of the AnyBlok project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Denis VIVIÈS <dvivies@geoblink.com>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import logging
import pytest
from . import add_complexe_model, add_simple_model
from anyblok.tests.conftest import *  # noqa
from anyblok.tests.conftest import init_registry

logger = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def registry_complexe_model(request, bloks_loaded):
    registry = init_registry(add_complexe_model)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_simple_model(request, bloks_loaded):
    registry = init_registry(add_simple_model)
    request.addfinalizer(registry.close)
    return registry
