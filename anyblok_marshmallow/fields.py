# This file is a part of the AnyBlok / Marshmallow api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from marshmallow.fields import Nested as FieldNested


class Nested(FieldNested):
    """Inherit marshmallow fields.Nested"""

    @property
    def schema(self):
        """Overload the super property to remove cache

        it is the only way to propagate the context at each call
        """
        self.__schema = None
        return super(Nested, self).schema
