#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOCS
# =============================================================================

__doc__ = """Installer logic

"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import subprocess
import atexit
import string
import urllib2
import urlparse
import json
import glob
import sys
import datetime
import zipfile

try:
    import cPickle as pickle
except ImportError:
    import pickle

from . import cons, ctx, db
from .libs import pypi, cache


# =============================================================================
# LOGGER and I18N
# =============================================================================

logger = cons.logger

_ = cons.I18N.gettext


# =============================================================================
# EXCEPTION
# =============================================================================

class InstallError(Exception):
    """This exception is raised when something gone wrong on install logic

    """

    def __init__(self, code):
        self.code = code
        super(InstallError, self).__init__(
            _("Exit code with value '{}'").format(code)
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

@cache.memoize(60, "seconds")
def check_connectivity(timeout=1):
    """Check if all servers needed for use oTree-launcher are online

    """
    errors = []
    for server in cons.SERVERS:
        try:
            urllib2.urlopen(server, timeout=timeout)
        except urllib2.URLError:
            host = urlparse.urlsplit(server).netloc
            errors.append(_("'{}' is unreachable").format(host))
    if errors:
        errors_joined = "\n  ".join(errors)
        msg = _("Check your internet connection\n  {}").format(errors_joined)
        raise IOError(msg)


def kill_proc(proc):
    if cons.IS_WINDOWS:
        proc = call(["TASKKILL", "/F", "/PID", str(proc.pid), "/T"])
        proc.communicate()
    else:
        import signal
        os.killpg(proc.pid, signal.SIGTERM)


def clean_proc(proc):
    """Clean process if is still runing on exit"""
    if proc.poll() is None:
        kill_proc(proc)


def call(command, *args, **kwargs):
    """Call an external command"""
    cleaned_cmd = [cmd.strip() for cmd in command if cmd.strip()]
    if cons.IS_WINDOWS:
        win_cmd = "{} < Nul".format(" ".join(cleaned_cmd))
        proc = subprocess.Popen(win_cmd, shell=True, *args, **kwargs)
    else:
        proc = subprocess.Popen(
            cleaned_cmd, preexec_fn=os.setsid, *args, **kwargs
        )
    atexit.register(clean_proc, proc)
    return proc


def render(template, wrkpath, decorate=True, **kwargs):
    """Render template acoring the working path

    """
    # vars
    context = {
        k: v for k, v in vars(cons).items()
        if not k.startswith("_") and k.isupper()
    }
    context.update({
        "WRK_PATH": wrkpath.replace("/", os.path.sep),
        "REQUIREMENTS_PATH": os.path.join(wrkpath, cons.REQUIREMENTS_FNAME),
        "OTREE_SCRIPT_PATH": os.path.join(wrkpath, cons.OTREE_SCRIPT_FNAME),
    })
    context.update(kwargs)

    src = string.Template(template.strip()).substitute(**context)

    if decorate:
        script = "".join(
            ["\n".join(cons.SCRIPT_HEADER), "\n"] +
            ["{}{}".format(l.strip(), cons.END_CMD)
             for l in src.splitlines()] +
            ["\n".join(cons.SCRIPT_FOOTER), "\n"]
        )
    else:
        script = "\n".join([l.strip() for l in src.splitlines()])
    return script.strip() + "\n"


# =============================================================================
# LOGIC ITSELF
# =============================================================================

def create_virtualenv():
    """Create otree virtualenv

    """
    logger.info(
        "Creating virtualenv in '{}'...".format(cons.LAUNCHER_VENV_PATH)
    )

    reqpath = None
    with ctx.tempfile("requirements", "txt") as fpath:
        logger.info(_("Downloading requirements file..."))
        with ctx.urlget(cons.VENV_REQUIREMENTS_URL) as response:
            with ctx.open(fpath, "w") as fp:
                fp.write(response.read())
        reqpath = fpath

    with ctx.tempfile("venv_installer", cons.SCRIPT_EXTENSION) as fpath:
        logger.info(_("Creating virtualenv install script..."))
        with ctx.open(fpath, "w") as fp:
            src = render(cons.CREATE_VENV_CMDS_TEMPLATE,
                         cons.LAUNCHER_VENV_PATH, REQUIREMENTS_PATH=reqpath)
            fp.write(src)
        logger.info(_("Creating venv, please wait"
                      " (this may take a few minutes)..."))
        return call([cons.INTERPRETER, fpath])


def clone(wrkpath):
    """Clone otree code into working dir

    """
    logger.info(_("Cloning into '{}'...").format(wrkpath))
    with ctx.tempfile("cloner", cons.SCRIPT_EXTENSION) as fpath:
        logger.info(_("Creating cloner script..."))
        with ctx.open(fpath, "w") as fp:
            src = render(cons.CLONE_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info(_("Cloning..."))
        return call([cons.INTERPRETER, fpath])


def install_requirements(wrkpath):
    """Intall the requirements of the given deploy

    """
    logger.info(
        _("Installing requirements in '{}'...").format(cons.LAUNCHER_VENV_PATH)
    )
    with ctx.tempfile("req_installer", cons.SCRIPT_EXTENSION) as fpath:
        logger.info(_("Creating requirements install script..."))
        with ctx.open(fpath, "w") as fp:
            src = render(cons.INSTALL_REQUIREMENTS_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info(_("Installing, please wait"
                      "(this may take a few minutes)..."))
        return call([cons.INTERPRETER, fpath])


def reset_db(wrkpath):
    """Reset the database of the oTree installation

    """
    logger.info(_("Reset oTree in '{}'...").format(wrkpath))
    with ctx.tempfile("reseter", cons.SCRIPT_EXTENSION) as fpath:
        logger.info(_("Creating reset script..."))
        with ctx.open(fpath, "w") as fp:
            src = render(cons.RESET_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info(_("Resetting (please wait)..."))
        return call([cons.INTERPRETER, fpath])


def runserver(wrkpath):
    """Run otree of the working path installation

    """
    logger.info(_("Running oTree in '{}'...").format(wrkpath))
    with ctx.tempfile("runner", cons.SCRIPT_EXTENSION) as fpath:
        logger.info(_("Creating runner script..."))
        with ctx.open(fpath, "w") as fp:
            src = render(cons.RUN_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info("Starting...")
        return call([cons.INTERPRETER, fpath])


def open_terminal(wrkpath):
    """Open a new terminal activating the virtualenv

    """
    logger.info("Opening terminal in '{}'...".format(wrkpath))
    with ctx.tempfile("open_terminal", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating open terminal script...")
        with ctx.open(fpath, "w") as fp:
            src = render(
                cons.OPEN_TERMINAL_CMDS_TEMPLATE, wrkpath, decorate=False
            )
            fp.write(src)
        logger.info("Launching Terminal...")
        return call([cons.INTERPRETER, fpath])


def open_filemanager(wrkpath):
    """Open a new terminal activating the virtualenv

    """
    logger.info("Opening filemanager in '{}'...".format(wrkpath))
    with ctx.tempfile("open_filemanager", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating open filemanager script...")
        with ctx.open(fpath, "w") as fp:
            src = render(
                cons.OPEN_FILEMANAGER_CMDS_TEMPLATE, wrkpath, decorate=False
            )
            fp.write(src)
        logger.info("Launching filemanager...")
        return call([cons.INTERPRETER, fpath])


def get_conf():
    """Get the configuration of oTree Launcher"""
    if db.Configuration.select().count():
            return db.Configuration.select().get()
    return db.Configuration.create()


def clean_logs(older_than=7):
    """Remove all log files older than 'older_than' days"""

    logger.info(
        "Cleaning older than {} days from dir '{}'".format(
            older_than, cons.LOG_DIR_PATH)
    )

    flt = os.path.join(cons.LOG_DIR_PATH, "*.log")
    for fpath in glob.glob(flt):
        if os.path.isfile(fpath):
            fname = os.path.basename(fpath)
            str_date = os.path.splitext(fname)[0]
            date = datetime.datetime.strptime(str_date, cons.DATE_FORMAT)
            if (cons.TODAY - date.date()).days > older_than:
                os.remove(fpath)


def logfile_fp(rewind=False):
    """Open and return the log file used for external process"""

    logger.info("Opening log file '{}'...".format(cons.LOG_FPATH))

    if not os.path.exists(cons.LOG_FPATH):
        with open(cons.LOG_FPATH, "w"):
            pass

    fp = open(cons.LOG_FPATH)
    if not rewind:
        fp.seek(0, 2)
    return fp


def clean_tempdir():
    """Destroy all files inside the temporary directory"""
    logger.info("Cleaning temp dir '{}'".format(cons.LAUNCHER_TEMP_DIR_PATH))
    for fname in os.listdir(cons.LAUNCHER_TEMP_DIR_PATH):
        fpath = os.path.join(cons.LAUNCHER_TEMP_DIR_PATH, fname)
        if os.path.isfile(fpath):
            os.remove(fpath)


@cache.memoize(30, "minutes")
def check_upgrade():
    """Chek if a new version of oTree-Launcher is available and if mandatory
    to upgrade the program

    Returns: last_version, is_new, mandatory
    """
    version = list(cons.VERSION)
    with ctx.urlget(cons.LASTEST_VERSION_URL) as response:
        data = json.load(response)

        lversion = data["version"]
        str_lversion = ".".join(lversion)

        exists_upgrade = version < lversion

        mcondition = data["mandatory"]["condition"]
        mvalue = data["mandatory"]["value"]

        mandatory = {
            "==": version == mvalue,
            "<": version < mvalue,
            "<=": version <= mvalue,
            ">": version > mvalue,
            ">=": version >= mvalue,
            "!=": version != mvalue,
            "in": version in mvalue
        }[mcondition]

        return str_lversion, exists_upgrade, mandatory


def otree_core_version(wrkpath):
    """Retrieve the otree-core version installed in the current project

    """
    logger.info("Retrieving otree-core version '{}'...".format(wrkpath))
    with ctx.tempfile("otree_core_version", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating otree-core version retriever script...")
        with ctx.open(fpath, "w") as fp:
            src = render(
                cons.OTREE_CORE_VERSION_CMDS_TEMPLATE, wrkpath, decorate=False)
            fp.write(src)
        proc = call([cons.INTERPRETER, fpath], stdout=subprocess.PIPE)
        out, _ = proc.communicate()
    for line in out.splitlines():
        line = line.strip()
        if line and line.startswith("otree-core"):
            ver = line.split(" ", 1)[-1]
            clean = ver[1:-1]
            return tuple(clean.split("."))


@cache.memoize(1, "hours")
def available_otree_core_versions():
    """Return a list of available versions of otree-core in pypi

    """
    logger.info("Retrieving available otree-core version on PyPi...")
    data = pypi.info("otree-core")
    versions = [tuple(ver.split(".")) for ver in data["releases"].keys()]
    versions.sort(reverse=True)
    return versions


def change_otree_core_version(wrkpath, version):
    """Patch the otree requirements_base.txt replacing the existing

    ``otree-core==OLD_VERSION``

    for

    ``otree-core==NEW_VERSION``

    and after that executing git commit

    """
    str_version = ".".join(version)
    requirements_path = os.path.join(wrkpath, cons.REQUIREMENTS_FNAME)

    old_version = None
    lines = []
    with ctx.open(requirements_path, "r") as fp:
        logger.info("Retrieving '{}'...".format(requirements_path))
        for line in fp.readlines():
            if line.startswith("otree-core=="):
                old_version = line.split("==", 1)[-1]
                line = "otree-core=={}".format(str_version)
            lines.append(line)

    with ctx.open(requirements_path, "w") as fp:
        logger.info("Writing new '{}'...".format(requirements_path))
        fp.writelines(lines)

    with ctx.tempfile("commit", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating commit script...")
        with ctx.open(fpath, "w") as fp:
            src = render(
                cons.GIT_COMMIT_REQUIREMENTS_CMDS_TEMPLATE, wrkpath,
                old_version=old_version, new_version=str_version)
            fp.write(src)
        logger.info("Commiting...")
        return call([cons.INTERPRETER, fpath])


def check_py_version():
    """Check if python version is ok for oTree-Launcher

    Returns: is_version_allowed(boolean), version_info, executable_path

    """
    allowed = (cons.MAX_PYVERSION == sys.version_info[:2])
    info = (allowed, sys.version, sys.executable)
    return info


def check_our_path():
    """Check if the oTree-Launcher is in valid path"""
    if " " in cons.OUR_PATH:
        return False
    try:
        cons.OUR_PATH.encode("ascii")
    except UnicodeError:
        return False
    return True


def zip_info(fpath):
    """Create a zip file with all the logs and temp_files of launcher"""

    def cons_as_pickle():
        cdict = {
            k: v for k, v in vars(cons).items()
            if not k.startswith("_") and k.isupper()}
        return pickle.dumps(cdict)

    with zipfile.ZipFile(fpath, 'w') as ziph:
        for root, dirs, files in os.walk(cons.LOG_DIR_PATH):
            for fname in files:
                fpath = os.path.join(root, fname)
                arcname = os.path.join("logs", fname)
                ziph.write(fpath, arcname)
        for root, dirs, files in os.walk(cons.LAUNCHER_TEMP_DIR_PATH):
            for fname in files:
                fpath = os.path.join(root, fname)
                arcname = os.path.join("temp", fname)
                ziph.write(fpath, arcname)
        if os.path.isfile(cons.DB_FPATH):
            ziph.write(cons.DB_FPATH, os.path.basename(cons.DB_FPATH))
        ziph.writestr("cons.pkl", cons_as_pickle())


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
