#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURES
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOC
# =============================================================================

__doc__ = """Simple JSON based implementation for i18n

"""


# =============================================================================
# COMMON IMPORTS
# =============================================================================

import os
import json
import glob
import ast
import argparse
import pprint


# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_LANGUAGES = (
    [l.split("_", 1)[0] for l in os.environ.get('LANG', '').split(':')] +
    ["en"]
)

TRANSLATION_FUNCTIONS = set([
    '_',
    'gettext',
    'ngettext', 'ngettext_lazy',
    'npgettext', 'npgettext_lazy',
    'pgettext', 'pgettext_lazy',
    'ugettext', 'ugettext_lazy', 'ugettext_noop',
    'ungettext', 'ungettext_lazy',
])


# =============================================================================
# CLASS
# =============================================================================

class JI18N(object):

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
            if lang not in self.langs:
                continue
            try:
                with open(fpath) as fp:
                    translations[lang] = json.load(fp)
            except:
                print "Error on parsing language file '{}'".format(fpath)
        return translations

    def gettext(self, string):
        for lang in self.langs:
            response = self.translations.setdefault(lang, {}).get(string)
            if response:
                return response
        return string

    def exists_translation(self, string):
        statuses = {}
        for lang in self.langs:
            lang_exists = lang in self.translations
            translation_exists = False
            if lang_exists:
                translation_exists = string in self.translations[lang]
            statuses[lang] = {
                "lang_exist": lang_exists,
                "translation_exists": translation_exists}
        return statuses


# =============================================================================
# FUNCTIONS
# =============================================================================

def find_i18n_strings(fpath):
    with open(fpath) as fp:
        source = fp.read()

    module = ast.parse(source, fpath)

    for node in ast.walk(module):
        if not isinstance(node, ast.Call):
            continue
        elif not isinstance(node.func, ast.Name):
            # It isn't a simple name, can't deduce what function it is.
            continue
        elif node.func.id not in TRANSLATION_FUNCTIONS:
            continue

        if node.args:
            ts = node.args[0]
        elif node.keywords:
            kw = node.keywords[0]
            if kw.arg != "string":
                continue
            ts = kw.value

        yield (ts.lineno, ts.s)


def gen_lang(prj, outdir, lang):
    """Generates an ``lang``  translation file for a given project (``prj``)

    parameters
    ----------

    prj: path
        path to the project
    outdir: path
        path to store or update json based translation files
    lang: str
        isocode for create or update dictionary

    """
    lang = lang.lower()
    lang_path = os.path.join(outdir, "{}.json".format(lang))
    py_glob = os.path.join(prj, "*.py")

    translations = {}
    exists = os.path.isfile(lang_path)

    if exists:
        with open(lang_path) as fp:
            translations = json.load(fp)

    for fname in glob.glob(py_glob):
        for lineno, string in find_i18n_strings(fname):
            translations.setdefault(string, "")

    with open(lang_path, "w") as fp:
        json.dump(translations, fp, indent=2)

    print(
        "{} Language file for {} {} ({})".format(
            lang.upper(), prj, "updated" if exists else "created", lang_path))


def translate(outdir, string):
    j18n = JI18N(outdir)
    print("'{}' -> '{}'".format(string, j18n.gettext(string)))
    pprint.pprint(j18n.exists_translation(string))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers()

    mm_parser = subparsers.add_parser('makemessages')
    mm_parser.add_argument(
        'prj', metavar='PATH', help='Path of the python projec')
    mm_parser.add_argument(
        'outdir', metavar='PATH',
        help='Path for storage the JSON Based Internationalization')
    mm_parser.add_argument(
        'lang', metavar='LANGUAGE', help='Language code of the translation')
    mm_parser.set_defaults(func=lambda a: gen_lang(a.prj, a.outdir, a.lang))

    mm_parser = subparsers.add_parser('translate')
    mm_parser.add_argument(
        'outdir', metavar='PATH',
        help='Path where the JSON dictionaries are stored')
    mm_parser.add_argument(
        'string', metavar='STRING', help='string to translate')
    mm_parser.set_defaults(func=lambda a: translate(a.outdir, a.string))

    args = parser.parse_args()
    args.func(args)
