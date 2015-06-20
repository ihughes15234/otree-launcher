#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURES
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOC
# =============================================================================

__doc__ = """Simple cache decorator for oTree-launcher

"""


# =============================================================================
# IMPORTS
# =============================================================================

import functools
import time
from collections import namedtuple
try:
    import cPickle as pickle
except ImportError:
    import pickle


# =============================================================================
# MEMOIZE
# =============================================================================

Memo = namedtuple("Memo", ["ttd", "value"])


def memoize(ttl):
    """Dict cache for python functions.

    Fails if some of the parameter of the function is not pickleable.

    ttl is the time in second for the 'time to live' of the data

    Example
    -------

    >>> import time
    >>>
    >>> @memoize(60)  # sixty seconds
    ... def now():
    ...    return time.time()
    ...
    >>> now()
    1434838788.73
    >>> now() # the value is not calculated us the last one
    1434838788.73
    >>> # wait 60 seconds
    >>> now()
    1434838848.77


    """
    cache = {}

    def _dec(fnc):

        @functools.wraps(fnc)
        def _wraps(*args, **kwargs):
            key = pickle.dumps((args, kwargs))
            data = cache.get(key)
            if data is None or data.ttd < time.time():
                value = fnc(*args, **kwargs)
                data = Memo(ttd=time.time() + ttl, value=value)
                cache[key] = data
            return data.value

        return _wraps

    return _dec


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
