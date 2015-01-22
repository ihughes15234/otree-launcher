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
        self.console.insert(Tkinter.END, formattedMessage + "\n")
        self.console.configure(state=Tkinter.DISABLED)
        self.console.see(Tkinter.END)
        self.console.update()



# =============================================================================
# GUI
# =============================================================================

class LogDisplay(Tkinter.LabelFrame):
    """A simple 'console' to place at the bottom of a Tkinter window """

    def __init__(self, root, **options):
        Tkinter.LabelFrame.__init__(self, root, **options)
        self.console = Tkinter.Text(self, height=10)
        self.console.configure(state=Tkinter.DISABLED)
        self.console.configure(bg="#222222", fg="white")
        self.console.pack(fill=Tkinter.BOTH)


class OTreeLauncherFrame(Tkinter.Frame):

    def __init__(self, root):
        Tkinter.Frame.__init__(self, root)
        self.root = root

        # menu
        menu = Tkinter.Menu(self)
        root.config(menu=menu)

        deploy_menu = Tkinter.Menu(menu)
        deploy_menu.add_command(label="New Deploy", command=self.do_deploy)
        deploy_menu.add_separator()
        deploy_menu.add_command(label="Exit", command=self.do_exit)
        menu.add_cascade(label="Deploys", menu=deploy_menu)

        # components
        self.log_display = LogDisplay(root)
        self.log_display.pack()

    def do_exit(self):
        self.root.quit()

    def do_deploy(self):
        # define options for opening or saving a file
        options = {
            'parent': self,
            'initialdir': cons.HOME_DIR,
            'mustexist': False,
            'title': 'Select directory for install oTree'
        }
        wrkpath = None
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
                wrkpath = dpath
                break
        if wrkpath:
            try:
                core.full_install_and_run(wrkpath)
            except Exception as err:
                tkMessageBox.showerror("Something gone wrong", unicode(err))



def run():
    # create gui
    root = Tkinter.Tk()
    root.title("{} - v.{}".format(cons.PRJ, cons.STR_VERSION))

    # add main frame
    frame = OTreeLauncherFrame(root)
    frame.pack(**{'fill': Tkconstants.BOTH})

    # setup logger
    logger.handlers = []
    logger.addHandler(LoggingToGUI(frame.log_display.console))
    logger.info("oTree Launcher says 'Hello'")

    # start
    root.mainloop()


if __name__=='__main__':
  run()
