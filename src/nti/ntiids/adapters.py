#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.externalization.externalization import _choose_field

from nti.externalization.interfaces import IExternalOID
from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import StandardInternalFields

from nti.ntiids.ntiids import TYPE_OID
from nti.ntiids.ntiids import is_ntiid_of_type

from nti.ntiids.oids import to_external_ntiid_oid

StandardExternalFields_ID = StandardExternalFields.ID
StandardExternalFields_OID = StandardExternalFields.OID

StandardInternalFields_ID = StandardInternalFields.ID


@interface.implementer(IExternalOID)
class _DefaultExternalOID(object):

    __slots__ = ('context',)

    def __init__(self, context):
        self.context = context

    def setOID(self, original, result):
        context = self.context if original is None else original
        result_id = _choose_field(result, context, StandardExternalFields_ID,
                                  fields=(StandardInternalFields_ID, StandardExternalFields_ID))
        # As we transition over to structured IDs that contain OIDs,
        # we'll try to use that for both the ID and OID portions
        if is_ntiid_of_type(result_id, TYPE_OID):
            # If we are trying to use OIDs as IDs, it's possible that the
            # ids are in the old, version 1 format, without an intid component.
            # If that's the case, then update them on the fly, but only for notes
            # because odd things happen to other  objects (chat rooms?)
            # if we do this to them
            if self.__class__.__name__ == 'Note':
                result_id = result[StandardExternalFields_ID]
                std_oid = to_external_ntiid_oid(self)
                if std_oid and std_oid.startswith(result_id):
                    result[StandardExternalFields_ID] = std_oid
            oid = result[StandardExternalFields_OID] = result[StandardExternalFields_ID]
        else:
            oid = to_external_ntiid_oid(self, default_oid=None)
            if oid:
                result[StandardExternalFields_OID] = oid
        return oid
