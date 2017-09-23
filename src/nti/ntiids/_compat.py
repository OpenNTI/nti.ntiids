#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six


def bytes_(s, encoding='utf-8', errors='strict'):
    """
    If ``s`` is an instance of ``text_type``, return
    ``s.encode(encoding, errors)``, otherwise return ``s``
    """
    if isinstance(s, six.text_type):
        return s.encode(encoding, errors)
    return s


def text_(s, encoding='utf-8', err='strict'):
    """
    Decode a byte sequence and unicode the result
    """
    s = s.decode(encoding, err) if isinstance(s, bytes) else s
    return six.text_type(s) if s is not None else None
