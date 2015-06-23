#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURES
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOC
# =============================================================================

__doc__ = """Simple implementation for i18n

"""


# =============================================================================
# COMMON IMPORTS
# =============================================================================

import os
import json
import glob


# =============================================================================
# CONSTANTS
# =============================================================================

PATH = os.path.abspath(os.path.dirname(__file__))

JSON_GLOB = os.path.join(PATH, "*.json")

DEFAULT_LANGUAGES = (
    [l.split("_", 1)[0] for l in os.environ.get('LANG', '').split(':')] +
    ["en"]
)

TRANSLATIONS = {}

for fpath in glob.glob(JSON_GLOB):
    fname = os.path.basename(fpath)
    lang = os.path.splitext(fname)[0]
    try:
        with open(fpath) as fp:
            code = "\n".join([
                line for line in fp.readlines()
                if not line.strip().startswith("#")
            ])
            TRANSLATIONS[lang] = json.loads(code)
    except Exception as err:
        print "Error on parsing language file '{}'".format(fpath)

# =============================================================================
# FUNCTIONS
# =============================================================================

def gettext(string):
    for lang in DEFAULT_LANGUAGES:
        response = TRANSLATIONS.setdefault(lang, {}).get(string)
        if response:
            return response
    return string


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)




