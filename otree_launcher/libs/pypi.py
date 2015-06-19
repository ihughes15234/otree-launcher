#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from . import six
from .six.moves import urllib


# =============================================================================
# CONSTANTS
# =============================================================================

INFO_URL_TEMPLATE = six.u("https://pypi.python.org/pypi/{package}/json")

INFO_VERSION_URL_TEMPLATE = six.u(
    "https://pypi.python.org/pypi/{package}/{version}/json")


# =============================================================================
# FUNCTION
# =============================================================================

def info(package, version=None):
    if version is None:
        url = INFO_URL_TEMPLATE.format(package=package)
    else:
        url = INFO_VERSION_URL_TEMPLATE.format(
            package=package, version=version)
    response = urllib.request.urlopen(url)
    try:
        info = json.load(response)
    finally:
        response.close()
    return info
