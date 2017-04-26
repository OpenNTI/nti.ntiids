#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id: __init__.py 104508 2017-01-17 04:20:48Z carlos.sanchez $
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import zope.i18nmessageid
MessageFactory = zope.i18nmessageid.MessageFactory('nti.ntiids')

from nti.ntiids.ntiids import find_object_with_ntiid
