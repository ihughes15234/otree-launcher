#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOCS
# =============================================================================

"""Command line interface

"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import argparse

from . import cons, core, gui, db


# =============================================================================
# CONSTANTS
# =============================================================================

logger = cons.logger


# =============================================================================
# FUNCTIONS
# =============================================================================

def get_parser():
    """Create a parser for install from command line

    """

    def dirpath(value):
        value = os.path.abspath(value)
        if os.path.isdir(value):
            msg = "'{}' directory already exists".format(value)
            raise argparse.ArgumentTypeError(msg)
        os.makedirs(value)
        return value

    parser = argparse.ArgumentParser(
        prog=cons.PRJ, version=cons.STR_VERSION, description=cons.DOC
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--gui", dest="gui", action="store_true",
        help="execute the the visual enviroment of the installer"
    )
    group.add_argument(
        "-w", "--wrkpath", dest="wrkpath", type=dirpath,
        metavar="WORK_PATH", help="The directory must not exists "
    )
    group.add_argument(
        "-l", "--list", dest="list", action="store_true",
        help="Show alredy existing deploys"
    )
    group.add_argument(
        "-r", "--reset", dest="reset", type=int,
        metavar="DEPLOY_ID", help="Reset an existing deploy"
    )
    group.add_argument(
        "-x", "--execute", dest="execute", type=int,
        metavar="DEPLOY_ID", help="Run an existing deploy"
    )
    group.add_argument(
        "-d", "--delete", dest="delete", type=int,
        metavar="DEPLOY_ID", help="delete an existing deploy"
    )
    group.add_argument(
        "--clear", dest="clear", action="store_true",
        help="Clear all the deployment database"
    )
    return parser


def ask(question):
    return raw_input(question + " [Y|N]? ") == "Y"


def run():
    """Execute the command line installer

    """
    parser = get_parser()
    args = parser.parse_args()
    if args.gui:
        gui.run()
    elif args.list:
        for deploy in db.Deploy.select():
            logger.info(deploy.resume())
    elif args.execute or args.reset or args.delete:
        deploy = db.Deploy.get(id=args.execute or args.reset or args.delete)
        if args.execute:
            proc = core.execute(deploy.path)
            core.open_webbrowser()
            proc.wait()
        elif args.reset:
            core.reset(deploy.path)
        elif args.delete:
            if ask("Remove the deploy on '{}'".format(deploy.path)):
                deploy.delete_instance(True)
            else:
                logger.info("Aborted!")
    elif args.clear:
        if ask("Remove all deployment data"):
            db.clear_database()
        else:
            logger.info("Aborted!")
    elif args.wrkpath:
        proc = core.full_install_and_run(args.wrkpath)
        proc.wait()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
