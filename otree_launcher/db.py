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

    def resume(self):
        text = "{} - {} (Created at: {} - Last Update: {})".format(
            str(self.id).zfill(4), self.path.ljust(50),
            self.created_date.isoformat().rsplit(".", 1)[0],
            self.last_update.isoformat().rsplit(".", 1)[0]
        )
        return text


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
