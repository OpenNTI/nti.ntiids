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

from nti.ntiids.oids import setExternalIdentifiers

from nti.ntiids.tests import SharedConfiguringTestLayer


class TestOIDs(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_hookable(self):
        assert_that(set_external_identifiers,
                    has_property('implementation', is_(setExternalIdentifiers)))
    
    def test_to_external_ntiid_oid(self):
        pass
