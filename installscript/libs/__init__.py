#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from . import virtualenv

if sys.platform.startswith("win"):
    from . import pbs as sh
else:
    from . import sh
