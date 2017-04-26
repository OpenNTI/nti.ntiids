#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constants and types for dealing with our unique IDs.

.. $Id: ntiids.py 111454 2017-04-26 03:04:41Z carlos.sanchez $
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import re
import six
import time
import string
import numbers
import datetime
import warnings
import collections

from zope import component
from zope import interface

from zope.schema.interfaces import ValidationError

from nti.ntiids import MessageFactory as _

from nti.ntiids.interfaces import INTIID
from nti.ntiids.interfaces import INTIIDResolver

# Well-known IDs
DATE = "2011-10"

#: prefix of NTIIDs
TAG_NTC = 'tag:nextthought.com'

#: When NTIIDs (usually of a particular type) are arranged into
#: a tree, or a forest of trees, this NTIID specifies the conceptual
#: root of the entire tree or forest.
ROOT = "%s,%s:Root" % (TAG_NTC, DATE)

#: Used as an opaque identifier to a specific object. This will
#: not incorporate the object's name or path (when those concepts make
#: sense). Instead, it points to an object by identity.
TYPE_OID = 'OID'

#: Meant to specify some sort of unique but otherwise
#: meaningless local portion. (Not necessarily an actual GUID).
TYPE_UUID = 'UUID'

#: The intid type is not currently used. Instead,
#: intid is included as a part of the OID, preventing
#: access using a stale URL after an object is deleted
TYPE_INTID = 'INTID'

#: Used as an opaque identifier to refer to an object that was
#: once (weakly) referenced, but can no longer be found. Only the system
#: will ever generate these, and these are never valid to send
#: as input to the system; they can never be resolved.
#: In general, references to the same missing object will produce
#: the same missing NTIID; however, in some cases, it may be possible
#: for references to different missing objects to produce the same missing
#: NTIID. Context will usually make it clear if this has happened.
TYPE_MISSING = 'Missing'

#: Named entities are globally accessible knowing nothing
#: more than a simple string name. There should be a defined
#: subtype for each namespace and/or specific kind of
#: named entity
TYPE_NAMED_ENTITY = 'NamedEntity'

#: Subtype of named entities identifying a particular user account
TYPE_NAMED_ENTITY_USER = TYPE_NAMED_ENTITY + ':User'

#: Subtype of named entities identifying a particular community
TYPE_NAMED_ENTITY_COMMUNITY = TYPE_NAMED_ENTITY + ':Community'

#: AKA an extant "chat" session
TYPE_ROOM = 'MeetingRoom'  
TYPE_MEETINGROOM = TYPE_ROOM

TYPE_HTML = 'HTML'
TYPE_QUIZ = 'Quiz'

TYPE_MEETINGROOM_GROUP = TYPE_ROOM + ':Group'

#: Transcripts and TranscriptSummaries. Note that
#: they are not subtypes of a common type because they
#: contain quite different information and are used
#: in different ways.
TYPE_TRANSCRIPT = 'Transcript'
TYPE_TRANSCRIPT_SUMMARY = 'TranscriptSummary'

# Validation
# This is a minimal set, required to make parsing wark;
# space is technically legal, but we escape it away anyway (?)
# Note specifically that neither path
# delimiter (forward or backward slash) is allowed as ntiids often
# wind up as filenames, and that would break many filename uses
_illegal_chars_ = r"/\";=?<>#%'{}|^[]"
_illegal_chars_pattern = r"[/\";=?<>#%'{}|^\[\]]"


class InvalidNTIIDError(ValidationError):
    """
    Raised if the NTIID value (or some part of it) is invalid.
    """


class ImpossibleToMakeSpecificPartSafe(InvalidNTIIDError):
    """
    The supplied value cannot be used safely.
    """

    i18n_message = _("The value you have used is not valid.")

ImpossibleToMakeProviderPartSafe = ImpossibleToMakeSpecificPartSafe


def validate_ntiid_string(ntiid):
    """
    Ensures the string is a valid NTIID, else raises :class:`InvalidNTIIDError`.

    :return: The `string`.
    """
    __traceback_info__ = ntiid,
    try:
        # cannot decode unicode
        ntiid = ntiid if isinstance(ntiid, six.text_type) else ntiid.decode('utf-8')
    except (AttributeError, TypeError):
        raise InvalidNTIIDError("Not a string " + repr(ntiid))
    except (UnicodeDecodeError,):
        raise InvalidNTIIDError("String contains non-utf-8 values " + 
                                repr(ntiid))

    if not ntiid or not ntiid.startswith('tag:nextthought.com,20'):
        raise InvalidNTIIDError('Missing correct start value: ' + repr(ntiid))

    # Split twice. Allow for : in the specific part
    parts = ntiid.split(':', 2)
    if len(parts) != 3:
        raise InvalidNTIIDError('Wrong number of colons: ' + ntiid)

    if len(parts[2].split('-')) > 3:
        raise InvalidNTIIDError('Wrong number of dashes: ' + ntiid)

    for char in _illegal_chars_:
        if char in ntiid:
            raise InvalidNTIIDError('Contains illegal char ' + repr(char))
    return ntiid

validate_ntiid_string(ROOT)


def is_valid_ntiid_string(ntiid):
    try:
        validate_ntiid_string(ntiid)
        return True
    except InvalidNTIIDError:
        return False


def is_ntiid_of_type(ntiid, nttype):
    """
    Check if the given ``ntiid`` is valid and of the given type
    (ignoring subtypes).

    :return: A True value if the ntiid is valid and has a type
            portion equivalent to the given nttype (i.e., ignoring
            subtypes).
    """
    return bool(nttype and is_ntiid_of_types(ntiid, (nttype,)))


def is_ntiid_of_types(ntiid, nttypes):
    """
    Check if the given ``ntiid`` is valid and of one of the given types
    (ignoring subtypes).

    :param nttypes: A sequence of types to check; they should not have
           subtypes.

    :return: A True value if the ntiid is valid and has a type
            portion equivalent to the given nttype (i.e., ignoring
            subtypes).
    """

    the_type = get_type(ntiid)
    if the_type:  # strip subtypes
        the_type = the_type.split(':', 2)[0]
        if the_type in nttypes:
            return the_type
    return None


def escape_provider(provider):
    """
    Makes a provider name safe for use in an NTIID by escaping
    characters not safe for a URL, such as _ and ' '. When
    comparing provider names with those that come fram an NTIID,
    you should always call this function.

    :return: The escaped provider, or the original value if it could not be escaped.

    """
    try:
        return re.sub('-', '_', re.sub('\s', '_', provider))
    except (TypeError, ValueError):
        return provider


def make_provider_safe(provider):
    """
    Given a potential provider part, transform it so that it is valid
    as part of an NTIID string.

    .. caution:: This is not a reversible transformation.
    """
    provider = re.sub(_illegal_chars_pattern, '_', provider)
    provider = escape_provider(provider)
    return provider

# TODO: A function to "escape" the local/specific part. Unfortunately, it's
# non-reversible so its less an escape and more a permutation.
# NOTE: While string.translate is tempting,
# it cannot be used because we allow the local parts to be Unicode and string.translate
# works on bytes.
# The below is a basic first pass, suitable for many uses, but not a
# complete solution

# We start by being extremely safe and limiting it to ascii letters and numbers,
# with no punctuation. There are some unicode characters that are dangerous
# and used in attacks on certain platforms (not to mention being confusing)

try:
    maketrans = string.maketrans
    translate = string.translate
except AttributeError:
    maketrans = str.maketrans
    translate = str.translate

_sp_repl_byte = '_'

_sp_strict_allowed = string.ascii_letters + string.digits
_sp_strict_removed = ''.join([chr(x) for x in range(0, 256) 
                              if chr(x) not in _sp_strict_allowed])
_sp_strict_transtable = maketrans(_sp_strict_removed,
                                  _sp_repl_byte * len(_sp_strict_removed))

# lax allows all non-control characters that are non-whitespace printable
# and not defined to be illegal
_sp_lax_allowed = [chr(x) for x in range(33, 128) 
                   if chr(x) not in (_illegal_chars_ + '-')]
_sp_lax_removed = ''.join([chr(x) for x in range(0, 256) 
                           if chr(x) not in _sp_lax_allowed])
_sp_lax_transtable = maketrans(_sp_lax_removed,
                               _sp_repl_byte * len(_sp_lax_removed))


def make_specific_safe(specific, strict=True):
    """
    Given a potential specific part, transform it so that it is valid
    as part of an NTIID string. This includes removing disallowed characters,
    and limiting the range of characters to printable ASCII compatible characters.

    .. caution:: This is not a reversible transformation.

    :keyword bool strict: If true (the default) then a maximally compatible set
            of characters will be substituted to make the safest part most
            likely to be parsed even by borderline parsers (such as those that
            are regex based). If set to false, however, only the minimal set of characters
            prohibited by the conforming parser implementation of this module will
            be replaced; typically only do this for backwards compatibility reasons.

    :raises InvalidNTIIDError: If this cannot be done. In particular, we refuse
            to create a safe part that consists entirely of the replacement characters;
            at least one character originally supplied must be valid. We also refuse
            to create a zero-length safe part.
    """

    # Since we are is ascii-land here, easy way to strip all high-chars is to
    # encode
    if not isinstance(specific, bytes):
        specific = specific.encode('ascii', 'ignore')
    if not isinstance(specific, six.string_types):
        specific = specific.decode('utf-8')

    table = _sp_strict_transtable if strict else _sp_lax_transtable
    specific = translate(specific, table)

    if not specific or set(specific) == set(_sp_repl_byte):
        raise ImpossibleToMakeSpecificPartSafe(specific)

    # back to unicode, coming from ascii
    try:
        return specific.decode('ascii')
    except AttributeError:
        return specific


def make_ntiid(date=DATE, provider=None, nttype=None, specific=None, base=None):
    """
    Create a new NTIID.

    :param number date: A value from :meth:`time.time`. If missing (0 or `None`), today will be used.
           If a string, then that string should be a portion of an ISO format date, e.g., 2011-10.
    :param str provider: Optional provider name. We will sanitize it for our format.
    :param str nttype: Required NTIID type (if no base is given)
    :param str specific: Optional type-specific part.
    :param str base: If given, an NTIID string from which provider, nttype, specific, and date
           will be taken if they are not directly specified. If not a valid NTIID, will be ignored.

    :return: A new NTIID string formatted as of the given date.
    """

    if base is not None and not is_valid_ntiid_string(base):
        base = None

    if not nttype and not base:
        raise ValueError('Must supply type')

    date_string = None
    if date is DATE and base is not None:
        date_string = get_parts(base).date
    elif isinstance(date, six.string_types):
        date_string = date
    else:
        # Account for 0/None
        if isinstance(date, numbers.Real) and date > 0:
            date_seconds = date
        else:
            date_seconds = time.time()

        # Always get the date in UTC/GMT by converting the epoch into a GMT tuple.
        # Then turn into a date object since that's the easiest way to get ISO
        # format.
        date = datetime.date(*time.gmtime(date_seconds)[0:3])
        date_string = date.isoformat()

    if date_string is None:
        __traceback_info__ = date, base
        raise ValueError("Unable to derive date string")

    base_parts = get_parts(base)

    # TODO: This is not a reversible transformation. Who should do this?
    if provider:
        if isinstance(provider, six.string_types):
            provider = provider.encode('ascii', 'ignore')
        else:
            provider = str(provider)
        if not isinstance(provider, six.string_types):
            provider = provider.decode("utf-8")
        provider = escape_provider(provider) + '-'
    else:
        provider = (base_parts.provider + '-' if base_parts.provider else '')
    
    if specific:
        specific = '-' +  specific 
    else:
        specific = ('-' + base_parts.specific if base_parts.specific else '')
    nttype = nttype or base_parts.nttype

    __traceback_info__ = (date_string, provider, nttype, specific)
    result = 'tag:nextthought.com,%s:%s%s%s' % __traceback_info__
    validate_ntiid_string(result)
    return result

NTIID = collections.namedtuple('NTIID',
                               map(str, ['provider', 'nttype', 'specific', 'date']))
interface.classImplements(NTIID, INTIID)


def _parse(ntiid):
    """
    :return: 4-tuple (provider, type, specific, date)
    """
    try:
        validate_ntiid_string(ntiid)
        _, tag_part, our_parts = ntiid.split(':', 2)
        date = tag_part.split(',')[-1]
        our_parts = our_parts.split('-')
        if len(our_parts) == 1:
            # only the type
            return NTIID(None, our_parts[0], None, date)
        if len(our_parts) == 2:
            # type and type spec.
            return NTIID(None, our_parts[0], our_parts[1], date)
        return NTIID(our_parts[0], our_parts[1], our_parts[2], date)
    except (InvalidNTIIDError, ValueError):
        return NTIID(None, None, None, None)


def get_provider(ntiid):
    """
    :return: The string of the provider part of the ntiid if it could be parsed, else None.
    """
    return _parse(ntiid).provider


def get_type(ntiid):
    """
    :return: The string of the type part of the ntiid if it could be parsed, else None.
    """
    return _parse(ntiid).nttype


def get_specific(ntiid):
    """
    :return: The string of the type-specific part of the ntiid if it could be parsed, else None.
    """
    return _parse(ntiid).specific


def get_parts(ntiid):
    """
    :return: An NTIID named four-tuple (provider, type, type-specific, date) if the ntiid could be parsed,
            or named four-tuple of None.
    """
    return _parse(ntiid)


def find_object_with_ntiid(key, **kwargs):
    """
    Attempts to find an object with the given NTIID. No security is implied; traversal is not
    necessarily used.

    :param string key: The NTIID to find.
    :param dict kwargs: Keyword arguments; this is to assist translation from legacy APIs and
            they are not currently used. If you send any, :mod:`warnings` will issue a warning.
    :return: The object found, or None if no object can be found or the ntiid passed is invalid.
    """

    if not is_valid_ntiid_string(key):
        logger.warn("Invalid ntiid string %s", key)
        return None
    if kwargs:
        warnings.warn("Function currently takes no kwargs")

    ntiid = _parse(key)
    resolver = component.queryUtility(INTIIDResolver, name=ntiid.nttype)
    if not resolver:
        if ntiid.nttype != TYPE_UUID:
            logger.warn("No ntiid resolver for '%s' in '%s'", 
                        ntiid.nttype, key)
        return None
    result = resolver.resolve(key)
    return result
