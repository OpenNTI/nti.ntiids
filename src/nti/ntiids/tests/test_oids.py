#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import assert_that
from hamcrest import has_property

import fudge
import unittest

from nti.externalization.externalization import set_external_identifiers

from nti.ntiids.oids import to_external_ntiid_oid
from nti.ntiids.oids import setExternalIdentifiers

from nti.ntiids.tests import SharedConfiguringTestLayer


class TestOIDs(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_hookable(self):
        assert_that(set_external_identifiers,
                    has_property('implementation', is_(setExternalIdentifiers)))

    @fudge.patch('nti.ntiids.oids.toExternalOID')
    def test_to_external_ntiid_oid(self, mock_teo):
        mock_teo.is_callable().with_args().returns('0x01:666f6f')
        ntiid = to_external_ntiid_oid(object())
        assert_that(ntiid,
                    is_('tag:nextthought.com,2011-10:zope.security.management.system_user-OID-0x01:666f6f'))
