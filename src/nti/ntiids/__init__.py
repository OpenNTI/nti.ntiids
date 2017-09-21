#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import zope.i18nmessageid
MessageFactory = zope.i18nmessageid.MessageFactory('nti.ntiids')

# Set the correct OID hookable function
from nti.ntiids.oids import set_hook
set_hook()
del set_hook
