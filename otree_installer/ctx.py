#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOCS
# =============================================================================

__doc__ = """Context managers for simplify otree core code

"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import contextlib
import codecs
import uuid
import urllib2

from . import cons


# =============================================================================
# FUNCTIONS
# =============================================================================

@contextlib.contextmanager
def tempfile(wrkpath, prefix, extension):
    fname = "{}_{}.{}".format(prefix, uuid.uuid4().int, extension)
    fpath = os.path.join(wrkpath, fname)
    try:
        yield fpath
    finally:
        if os.path.isfile(fpath):
            os.remove(fpath)


@contextlib.contextmanager
def open(fname, mode, *args, **kwargs):
    if "encoding" not in kwargs:
        kwargs["encoding"] = cons.ENCODING
    with codecs.open(fname, mode, *args, **kwargs) as fp:
        yield fp


@contextlib.contextmanager
def urlget(url, *args, **kwargs):
    with contextlib.closing(urllib2.urlopen(url, *args, **kwargs)) as response:
        yield response


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
