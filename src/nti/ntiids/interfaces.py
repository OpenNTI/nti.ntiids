#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from zope import interface

from zope.interface.common.sequence import IMinimalSequence

from nti.schema.field import TextLine


class ITuple(interface.Interface):
    """
    Marker interface for tuples
    """
    def __iter__():
        """
        return an iterable of the items in the tuple
        """
interface.classImplements(tuple, ITuple)


class INTIID(ITuple, IMinimalSequence):
    """
    Represents the parts of an NTIID that has been parsed.

    In addition to the named fields, this object acts as a 4-tuple,
    (provider, type, specific, date)
    """
    provider = TextLine(title=u"The username of the creating/providing entity.")

    nttype = TextLine(title=u"The type of the NTIID.")

    specific = TextLine(title=u"The type-specific portion of the NTIID.")

    date = TextLine(title=u"The date portion of the NTIID.")


class INTIIDResolver(interface.Interface):
    """
    An object that can take an NTIID and produce the object
    to which it refers.

    These should be registered as components named for the ntiid type (e.g, OID).
    """

    def resolve(ntiid_string):
        """
        :return: The object to which the `ntiid_string` refers,
                 or None if it cannot be found.
        """
