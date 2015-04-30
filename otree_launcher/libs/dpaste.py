#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import urllib
import urllib2


DPASTE_URL = "http://dpaste.com/api/v2/"

DPASTE_OK_CODE = 201


def paste(content, syntax="text", title=None, poster=None, expiry_days=1):
    data = {"content": content, "syntax": syntax, "expiry_days": expiry_days}
    if title:
        data["title"] = title
    if poster:
        data["poster"] = poster

    encoded_data = urllib.urlencode(data)
    conn = urllib2.urlopen(DPASTE_URL, encoded_data)
    return conn.headers["location"]








