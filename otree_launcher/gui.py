#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURES
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOC
# =============================================================================

__doc__ = """Constants for all oTree launcher

"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import logging

import Tkinter
import Tkconstants
import tkMessageBox
import tkFileDialog

from . import cons, core


# =============================================================================
# LOGGER
# =============================================================================

logger = cons.logger


# =============================================================================
# LOGGER
# =============================================================================

class LoggingToGUI(logging.Handler):
    """ Used to redirect logging output to the widget passed in parameters

    Based on http://goo.gl/LrxkGZ

    """

    def __init__(self, console):
        super(LoggingToGUI, self).__init__()
        self.console = console

    def emit(self, message):
        formattedMessage = self.format(message)
        self.console.configure(state=Tkinter.NORMAL)
        self.console.insert(Tkinter.END, formattedMessage)
        self.console.configure(state=Tkinter.DISABLED)
        self.console.see(Tkinter.END)



# =============================================================================
# GUI
# =============================================================================

class LogDisplay(Tkinter.LabelFrame):
    """A simple 'console' to place at the bottom of a Tkinter window """

    def __init__(self, root, **options):
        Tkinter.LabelFrame.__init__(self, root, **options);
        self.console = Tkinter.Text(self, height=10)
        self.console.pack(fill=Tkinter.BOTH)
        self.console.configure(state=Tkinter.DISABLED)


def ask_directory(parent):
    # define options for opening or saving a file
    options = {
        'parent': parent,
        'initialdir': cons.HOME_DIR,
        'mustexist': False,
        'title': 'Select directory for install oTree'
    }
    while True:
        dpath = tkFileDialog.askdirectory(**options)
        if not dpath:
            return None
        elif not os.path.isdir(dpath):
            os.makedirs(dpath)
        if len(os.listdir(dpath)):
            options["initialdir"] = dpath
            msg = "Please select an empty directory"
            tkMessageBox.showerror("Directory is not empty", msg)
        else:
            return dpath

def run():
    root = Tkinter.Tk()
    log_display = LogDisplay(root)
    log_display.pack()
    logger.addHandler(LoggingToGUI(log_display.console))
    logger.info("puto")

    wrkpath = ask_directory(root)
    if wrkpath:
        core.full_install_and_run(wrkpath)

    root.destroy()
    root.mainloop()


if __name__=='__main__':
  run()
