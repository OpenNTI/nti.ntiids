#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import raises
from hamcrest import calling
from hamcrest import assert_that
from hamcrest import has_property

from nti.testing.matchers import verifiably_provides

import time
import datetime
from unittest import TestCase

from nti.ntiids import ntiids

from nti.ntiids import interfaces

from nti.ntiids.tests import SharedConfiguringTestLayer


class TestNTIIDS(TestCase):

    layer = SharedConfiguringTestLayer

    def test_make_ntiid(self):
        self.assertRaises(ValueError, ntiids.make_ntiid)
        self.assertRaises(ValueError, 
                          ntiids.make_ntiid, 
                          provider='foo', 
                          specific='baz')
        iso_now = datetime.date(*time.gmtime()[:3]).isoformat()

        assert_that(ntiids.make_ntiid(date=None, nttype='Test'),
                    is_('tag:nextthought.com,%s:Test' % iso_now))

        assert_that(ntiids.make_ntiid(date=0, nttype='Test'),
                    is_('tag:nextthought.com,%s:Test' % iso_now))

        assert_that(ntiids.make_ntiid(date=None, nttype='Test', provider='TestP'),
                    is_('tag:nextthought.com,%s:TestP-Test' % iso_now))

        assert_that(ntiids.make_ntiid(date=None, nttype='Test', provider='TestP', specific='Bar'),
                    is_('tag:nextthought.com,%s:TestP-Test-Bar' % iso_now))

        assert_that(ntiids.make_ntiid(date=None,
                                      nttype='Test',
                                      provider=u'Henry Beach Needham . McClure\u2019s Magazine',
                                      specific='Bar'),
                    is_('tag:nextthought.com,%s:Henry_Beach_Needham_._McClures_Magazine-Test-Bar' % iso_now))

    def test_parse_ntiid(self):
        ntiid = ntiids.get_parts(ntiids.ROOT)
        assert_that(ntiid, verifiably_provides(interfaces.INTIID))

        ntiid = 'tag:nextthought.com,2011-10:Foo-Bar-With:Many:Colons'
        ntiids.validate_ntiid_string(ntiid)

        ntiid = ntiids.get_parts(ntiid)
        assert_that(ntiid, has_property('provider', 'Foo'))
        assert_that(ntiid, has_property('nttype', 'Bar'))
        assert_that(ntiid, has_property('specific', 'With:Many:Colons'))

    def test_utc_date(self):
        #"A timestamp should always be interpreted UTC."
        # This date is 2012-01-05 in UTC, but 2012-01-04 in CST
        assert_that(ntiids.make_ntiid(date=1325723859.140755, nttype='Test'),
                    is_('tag:nextthought.com,2012-01-05:Test'))

    def test_make_safe(self):
        assert_that(ntiids.make_specific_safe('-Foo%Bar +baz:?'),
                    is_('_Foo_Bar__baz__'))
        assert_that(ntiids.make_specific_safe('-Foo%Bar/+baz:?'),
                    is_('_Foo_Bar__baz__'))

        # lax lets more through
        assert_that(ntiids.make_specific_safe('-Foo%Bar, +baz:?', strict=False),
                    is_('_Foo_Bar,_+baz:_'))

        # too short
        assert_that(calling(ntiids.make_specific_safe).with_args(''),
                    raises(ntiids.ImpossibleToMakeSpecificPartSafe))
        # only invalid characters
        assert_that(calling(ntiids.make_specific_safe).with_args('     '),
                    raises(ntiids.ImpossibleToMakeSpecificPartSafe))

        assert_that(calling(ntiids.make_specific_safe).with_args('Алибра школа'),
                    raises(ntiids.ImpossibleToMakeSpecificPartSafe))

        assert_that(ntiids.make_provider_safe('NSF/[Science]Nation?'),
                    is_('NSF__Science_Nation_'))
