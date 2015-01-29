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
import sys

from . import cons


# =============================================================================
# FUNCTIONS
# =============================================================================

@contextlib.contextmanager
def tempfile(prefix, extension):
    """Create a temporary fule in the wrkpath

    """
    fname = "{}_{}.{}".format(prefix, uuid.uuid4().int, extension)
    fpath = os.path.join(cons.LAUNCHER_TEMP_DIR_PATH, fname)
    try:
        yield fpath
    finally:
        if os.path.isfile(fpath):
            os.remove(fpath)


@contextlib.contextmanager
def open(fname, mode, *args, **kwargs):
    """Open a file. If encoding is not seted the default encoding is used

    """
    if "encoding" not in kwargs:
        kwargs["encoding"] = cons.ENCODING
    with codecs.open(fname, mode, *args, **kwargs) as fp:
        yield fp


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
