#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

import unittest

from zope.schema.interfaces import InvalidURI

from nti.ntiids.schema import ValidNTIID

from nti.ntiids.tests import SharedConfiguringTestLayer


class TestSchema(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_schema(self):
        nti = 'tag:nextthought.com,2011-10:zope.security.management.system_user-OID-0x01:666f6f'
        schema = ValidNTIID()
        schema.fromUnicode(nti)
        with self.assertRaises(InvalidURI):
            schema.fromUnicode('xx')
