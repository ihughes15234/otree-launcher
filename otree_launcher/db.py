#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOCS
# =============================================================================

"""Database interface for otree launcher

"""


# =============================================================================
# IMPORTS
# =============================================================================

import datetime

from . import cons
from .libs import peewee


# =============================================================================
# CONSTANTS
# =============================================================================

logger = cons.logger


# =============================================================================
# CONSTANTS
# =============================================================================

DB = peewee.SqliteDatabase(cons.DB_PATH, threadlocals=True)


# =============================================================================
# MODELS
# =============================================================================

class BaseModel(peewee.Model):
    class Meta:
        database = DB


class Deploy(BaseModel):

    path = peewee.TextField()
    created_date = peewee.DateTimeField(default=datetime.datetime.now)
    last_update = peewee.DateTimeField(default=datetime.datetime.now)
    selected = peewee.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super(Deploy, self).save(*args, **kwargs)
        if self.selected:
            Deploy.update(
                selected=False
            ).where(
                Deploy.id != self.id
            ).execute()


# =============================================================================
# SETUP
# =============================================================================

DB.connect()

def create_tables():
    for cls in BaseModel.__subclasses__():
        cls.create_table(fail_silently=True)

def clear_database():
    logger.info("Removing data...")
    DB.drop_tables(BaseModel.__subclasses__())
    create_tables()

create_tables()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
