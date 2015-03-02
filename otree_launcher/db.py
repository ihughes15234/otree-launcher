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

from . import cons
from .libs import peewee


# =============================================================================
# CONSTANTS
# =============================================================================

logger = cons.logger


# =============================================================================
# CONSTANTS
# =============================================================================

DB = peewee.SqliteDatabase(cons.DB_FPATH, threadlocals=True)


# =============================================================================
# MODELS
# =============================================================================

class BaseModel(peewee.Model):
    class Meta:
        database = DB


class Configuration(BaseModel):

    path = peewee.TextField(null=True)
    virtualenv = peewee.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id and Configuration.select().count():
            msg = "only one configuration is allowed"
            raise ValueError(msg)
        super(Configuration, self).save(*args, **kwargs)


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
