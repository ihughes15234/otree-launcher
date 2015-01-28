#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURES
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOC
# =============================================================================

__doc__ = """Entry point of oTree installer

"""


# =============================================================================
# FUNCTIONS
# =============================================================================

def main():
    """Execute otree installer

    """
    from otree_launcher import core, cons
    wrkpath = r"c:\kkk" if cons.IS_WINDOWS else "/home/juan/kkk"
    proc = core.reset_db(wrkpath)
    proc.wait()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    main()
