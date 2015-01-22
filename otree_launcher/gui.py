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
import webbrowser

import Tkinter
import Tkconstants
import tkMessageBox
import tkFileDialog

from . import cons, core, db


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
        self.menu = Tkinter.Menu(self)
        root.config(menu=self.menu)

        deploy_menu = Tkinter.Menu(self.menu)
        deploy_menu.add_command(label="New Deploy", command=self.do_deploy)
        deploy_menu.add_separator()
        deploy_menu.add_command(label="Exit", command=self.do_exit)
        self.menu.add_cascade(label="Deploys", menu=deploy_menu)

        about_menu = Tkinter.Menu(self.menu)
        about_menu.add_command(
            label="oTree Homepage", command=self.do_open_homepage
        )
        about_menu.add_command(label="About me...", command=self.do_about)
        self.menu.add_cascade(label="About", menu=about_menu)

        # components
        self.deploys = []
        self.deploy_listbox = Tkinter.Listbox(self, selectmode=Tkinter.SINGLE)
        self.refresh_deploy_list()
        self.deploy_listbox.pack()

        self.log_display = LogDisplay(root)
        self.log_display.pack()

    def refresh_deploy_list(self):
        self.deploy_listbox.delete(0, len(self.deploys)-1)
        self.deploys = []
        for deploy in db.Deploy.select():
            text = "{} - {} (Created at: - Last Update: {})".format(
                deploy.id, deploy.path, deploy.created_date, deploy.last_update
            )
            self.deploy_listbox.insert(Tkinter.END, text)
            self.deploys.append(deploy)

    def do_about(self):
        title = "About {} - v.{}".format(cons.PRJ, cons.STR_VERSION)
        body = (
            "{doc}"
            "A modern open platform for social science experiment\n"
            "Version: {version}"
        ).format(prj=cons.PRJ, url=cons.URL, doc=cons.DOC, version=cons.STR_VERSION)
        tkMessageBox.showinfo(title, body)

    def do_open_homepage(self):
        webbrowser.open_new_tab(cons.URL)

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
                tkMessageBox.showwarning("Directory is not empty", msg)
            else:
                wrkpath = dpath
                break
        if wrkpath:
            try:
                core.full_install_and_run(wrkpath)
            except Exception as err:
                tkMessageBox.showerror("Something gone wrong", unicode(err))
            else:
                self.refresh_deploy_list()


# =============================================================================
# FUNCTIONS
# =============================================================================

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
