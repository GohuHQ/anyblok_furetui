# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from sqlalchemy import or_


@Declarations.register(Declarations.Core)
class Base:

    @classmethod
    def getPksFromFilters(cls, filters):
        raise Exception('No filter for no SQL Model')


@Declarations.register(Declarations.Core)
class SqlBase:

    @classmethod
    def _getPksFromFilterField(cls, query, field, operator, value):
        if isinstance(value, list):
            return query.filter(or_(*[field.ilike('%' + st + '%')
                                      for st in value]))

        return query.filter(field.ilike('%' + value + '%'))

    @classmethod
    def _getPksFromFilter(cls, query, keys, operator, value):
        field = getattr(cls, keys[0])
        if len(keys) == 1:
            query = cls._getPksFromFilterField(query, field, operator, value)
        else:
            query = query.join(field)
            Model = field.property.mapper.class_
            query = Model._getPksFromFilter(query, keys[1:], operator, value)

        return query

    @classmethod
    def getPksFromFilters(cls, filters):
        query = cls.query()
        for f in filters:
            query = cls._getPksFromFilter(
                query, f['key'].split('.'), f.get('operator', 'ilike'),
                f['value']
            )

        return [x.to_primary_keys() for x in query.all()]
