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
    from otree_installer import cli
    cli.run()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    main()