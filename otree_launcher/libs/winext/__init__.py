#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURES
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOC
# =============================================================================

__doc__ = """All windows common extensions"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import subprocess


# =============================================================================
# CONSTANTS
# =============================================================================

PATH = os.path.abspath(os.path.dirname(__file__))


# =============================================================================
# EXCEPTIONS
# =============================================================================

class CallError(Exception):

    def __init__(self, cmd, stderr, code):
        msg = "External call '{}' fail with code '{}'. Cause: '{}'".format(
            cmd, code, stderr)
        super(CallError, self).__init__(msg)
        self.cmd = cmd
        self.stderr = stderr
        self.code = code


# =============================================================================
# FUNCTIONS
# =============================================================================

def call(cmd):
    """Execute the cmd an return the standar output or raises an exception

    """
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode:
        raise CallError(cmd, stderr, p.returncode)
    return stdout

    
def shortpath(path):
    cmd = [os.path.join(PATH, "shortpath.bat"), path]
    out = call(cmd)
    return out.strip()
    
