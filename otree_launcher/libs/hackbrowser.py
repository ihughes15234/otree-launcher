#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOCS
# =============================================================================

__doc__ = """Webbroser don't work well in macosx so this file hack
this behavior

"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import sys
import webbrowser


# =============================================================================
# CONSTANTS
# =============================================================================

def open(url):
    if sys.platform.startswith("darwin"):
        cmd = "open {}".format(url)
        retcode = os.system(cmd)
        return (retcode == 0)
    return webbrowser.open_new_tab(url)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)