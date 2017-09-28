#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
does_not = is_not

import unittest

from nti.ntiids._compat import text_
from nti.ntiids._compat import bytes_


class TestCompat(unittest.TestCase):

    def test_bytes(self):
        assert_that(bytes_(u'\u2019'), is_(b'\xe2\x80\x99'))
        assert_that(text_(b'\xe2\x80\x99'), is_(u'\u2019'))
