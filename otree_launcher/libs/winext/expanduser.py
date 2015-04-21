#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on: http://stackoverflow.com/a/23889086/2489206

import os

import ctypes
from ctypes import windll, wintypes


class GUID(ctypes.Structure):
    _fields_ = [
         ('Data1', wintypes.DWORD),
         ('Data2', wintypes.WORD),
         ('Data3', wintypes.WORD),
         ('Data4', wintypes.BYTE * 8)
    ]

    def __init__(self, l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8):
        """Create a new GUID."""
        self.Data1 = l
        self.Data2 = w1
        self.Data3 = w2
        self.Data4[:] = (b1, b2, b3, b4, b5, b6, b7, b8)

    def __repr__(self):
        b1, b2, b3, b4, b5, b6, b7, b8 = self.Data4
        return 'GUID(%x-%x-%x-%x%x%x%x%x%x%x%x)' % (
                   self.Data1, self.Data2, self.Data3,
                   b1, b2, b3, b4, b5, b6, b7, b8)


# constants to be used according to the version on shell32
CSIDL_PROFILE = 40
FOLDERID_Profile = GUID(0x5E6C858F, 0x0E22, 0x4760, 0x9A, 0xFE,
                        0xEA, 0x33, 0x17, 0xB6, 0x71, 0x73)

def _expanduser(path):
    if path != "~":
        raise ValueError("Only '~' is allowed")

    # get the function that we can find from Vista up, not the one in XP
    get_folder_path = getattr(windll.shell32, 'SHGetKnownFolderPath', None)
    if get_folder_path is not None:
        # ok, we can use the new function which is recomended by the msdn
        ptr = ctypes.c_wchar_p()
        get_folder_path(ctypes.byref(FOLDERID_Profile), 0, 0, ctypes.byref(ptr))
        return ptr.value
    else:
        # use the deprecated one found in XP and on for compatibility reasons
       get_folder_path = getattr(windll.shell32, 'SHGetSpecialFolderPathW', None)
       buf = ctypes.create_unicode_buffer(300)
       get_folder_path(None, buf, CSIDL_PROFILE, False)
       return buf.value


def expanduser(path):
    try:
        return os.path.expanduser(path)
    except UnicodeDecodeError:
        return _expanduser(path)
