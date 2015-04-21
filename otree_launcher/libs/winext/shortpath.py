#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on: http://stackoverflow.com/a/23598461/200291

# =============================================================================
# FUTURES
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOC
# =============================================================================

__doc__ = """Short path"""


# =============================================================================
# IMPORTS
# =============================================================================

import ctypes
from ctypes import wintypes


# =============================================================================
# CONSTANTS
# =============================================================================

_GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
_GetShortPathNameW.argtypes = [
    wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
_GetShortPathNameW.restype = wintypes.DWORD


# =============================================================================
# FUNCTIONS
# =============================================================================

def shortpath(path):
    """
    Gets the short path name of a given long path.
    http://stackoverflow.com/a/23598461/200291
    """
    output_buf_size = 0
    while True:
        output_buf = ctypes.create_unicode_buffer(output_buf_size)
        needed = _GetShortPathNameW(path, output_buf, output_buf_size)
        if output_buf_size >= needed:
            return output_buf.value
        else:
            output_buf_size = needed

