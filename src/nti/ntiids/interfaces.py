#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NTIID related interfaces.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.interface.common.sequence import IMinimalSequence

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from dolmen.builtins import ITuple

from nti.schema.field import TextLine


class INTIID(ITuple, IMinimalSequence):
    """
    Represents the parts of an NTIID that has been parsed.

    In addition to the named fields, this object acts as a 4-tuple,
    (provider, type, specific, date)
    """
    provider = TextLine(title="The username of the creating/providing entity.")
    nttype = TextLine(title="The type of the NTIID.")
    specific = TextLine(title="The type-specific portion of the NTIID.")
    date = TextLine(title="The date portion of the NTIID.")


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

class IUpdateNTIIDEvent(IObjectEvent):

    old_ntiid = interface.Attribute("The previous ntiid")
    new_ntiid = interface.Attribute("The new ntiid")


class IWillUpdateNTIIDEvent(IUpdateNTIIDEvent):
    """
    An event that is sent when an ntiid for an object is about to change.
    """


class IUpdatedNTIIDEvent(IUpdateNTIIDEvent):
    """
    An event that is sent when an ntiid for an object has been changed.
    """


@interface.implementer(IWillUpdateNTIIDEvent)
class AbstractUpdateNTIIDEvent(ObjectEvent):

    def __init__(self, obj, old_ntiid, new_ntiid):
        super(AbstractUpdateNTIIDEvent, self).__init__(obj)
        self.old_ntiid = old_ntiid
        self.new_ntiid = new_ntiid


@interface.implementer(IWillUpdateNTIIDEvent)
class WillUpdateNTIIDEvent(AbstractUpdateNTIIDEvent):
    pass

@interface.implementer(IUpdatedNTIIDEvent)
class UpdatedNTIIDEvent(AbstractUpdateNTIIDEvent):
    pass
