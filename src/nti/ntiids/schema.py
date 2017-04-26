#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Support for using NTIIDs in a zope schema.

.. $Id: schema.py 104508 2017-01-17 04:20:48Z carlos.sanchez $
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

from nti.ntiids.ntiids import validate_ntiid_string

from nti.schema.field import ValidURI


class ValidNTIID(ValidURI):
    """
    A schema field that checks that the value is a correctly
    formed NTIID. (This does not perform any validation that the
    value is actually reachable or accessibly in a library or catalog.)
    """

    _type = six.text_type

    def fromUnicode(self, value):
        # The very first thing the superclass does is turn
        # the value into a bytestring again (under py2),
        # which is obviously wrong for us. So skip that.
        value = value.strip()
        self.validate(value)
        return value

    def _validate(self, value):
        super(ValidNTIID, self)._validate(value)
        validate_ntiid_string(value)
