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

DEFAULT_LANGUAGES = (
    [l.split("_", 1)[0] for l in os.environ.get('LANG', '').split(':')] +
    ["en"]
)


# =============================================================================
# TRANSLATION LOAD
# =============================================================================

class I18N(object):

    def __init__(self, langs_path, langs=[]):
        self.langs_path = langs_path
        self.langs = langs or DEFAULT_LANGUAGES
        self.translations = self.load_translations()

    def load_translations(self):
        json_glob = os.path.join(self.langs_path, "*.json")
        translations = {}
        for fpath in glob.glob(json_glob):
            fname = os.path.basename(fpath)
            lang = os.path.splitext(fname)[0]
            try:
                with open(fpath) as fp:
                    translations[lang] = i18njson_load(fp)
            except Exception as err:
                print "Error on parsing language file '{}'".format(fpath)
            return translations

    def gettext(self, string):
        for lang in DEFAULT_LANGUAGES:
            response = self.translations.setdefault(lang, {}).get(string)
            if response:
                return response
        return string


# =============================================================================
# FUNCTIONS
# =============================================================================

def i18njson_load(fp, *args, **kwargs):
    code = "\n".join([
        line for line in fp.readlines() if not line.strip().startswith("#")])
    return json.loads(code)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)




