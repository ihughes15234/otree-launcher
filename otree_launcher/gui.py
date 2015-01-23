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
import tkMessageBox
import tkFileDialog

from . import cons, core, db, res
from .libs import splash



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
        self.console.insert(Tkinter.END, "> " + formattedMessage + "\n")
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
        self.console.configure(bg="#222222", fg="#dddddd")
        self.console.pack(fill=Tkinter.BOTH, expand=True)


class OTreeLauncherFrame(Tkinter.Frame):

    def __init__(self, root):
        Tkinter.Frame.__init__(self, root)
        self.root = root

        # icons
        self.icon_new = Tkinter.PhotoImage(file=res.get("new.gif"))
        self.icon_clear = Tkinter.PhotoImage(file=res.get("clear.gif"))
        self.icon_exit = Tkinter.PhotoImage(file=res.get("exit.gif"))
        self.icon_homepage = Tkinter.PhotoImage(file=res.get("homepage.gif"))
        self.icon_about = Tkinter.PhotoImage(file=res.get("about.gif"))

        self.icon_run = Tkinter.PhotoImage(file=res.get("run.gif"))
        self.icon_delete = Tkinter.PhotoImage(file=res.get("delete.gif"))
        self.icon_reset = Tkinter.PhotoImage(file=res.get("reset.gif"))

        # menu
        self.menu = Tkinter.Menu(self)
        root.config(menu=self.menu)

        deploy_menu = Tkinter.Menu(self.menu)
        deploy_menu.add_command(
            label="New Deploy", command=self.do_deploy,
            compound=Tkinter.LEFT, image=self.icon_new
        )
        deploy_menu.add_separator()
        deploy_menu.add_command(
            label="Clear deploy database", command=self.do_clear,
            compound=Tkinter.LEFT, image=self.icon_clear
        )
        deploy_menu.add_separator()
        deploy_menu.add_command(
            label="Exit", command=self.do_exit,
            compound=Tkinter.LEFT, image=self.icon_exit
        )
        self.menu.add_cascade(label="Deploys", menu=deploy_menu)

        about_menu = Tkinter.Menu(self.menu)
        about_menu.add_command(
            label="oTree Homepage", command=self.do_open_homepage,
            compound=Tkinter.LEFT, image=self.icon_homepage
        )
        about_menu.add_command(
            label="About me...", command=self.do_about,
            compound=Tkinter.LEFT, image=self.icon_about
        )
        self.menu.add_cascade(label="About", menu=about_menu)

        # components
        self.deploys = []

        listFrame = Tkinter.Frame(self)
        listFrame.pack(fill=Tkinter.BOTH, expand=True)
        scrollBar = Tkinter.Scrollbar(listFrame)
        scrollBar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

        self.deploy_listbox = Tkinter.Listbox(
            listFrame, selectmode=Tkinter.SINGLE
        )
        self.refresh_deploy_list()
        self.deploy_listbox.pack(
            side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=True
        )

        scrollBar.config(command=self.deploy_listbox.yview)
        self.deploy_listbox.config(yscrollcommand=scrollBar.set)

        btnFrame = Tkinter.Frame(self)
        btnFrame.pack(fill=Tkinter.X)
        self.run_button = Tkinter.Button(
            btnFrame, text="Run Selected Deploy", command=self.do_run,
            compound=Tkinter.LEFT, image=self.icon_run
        )
        self.run_button.pack(side=Tkinter.RIGHT)
        self.reset_button = Tkinter.Button(
            btnFrame, text="Reset Selected Deploy", command=self.do_reset,
            compound=Tkinter.LEFT, image=self.icon_reset
        )
        self.reset_button.pack(side=Tkinter.RIGHT)
        self.delete_button = Tkinter.Button(
            btnFrame, text="Delete Selected Deploy", command=self.do_delete,
            compound=Tkinter.LEFT, image=self.icon_delete
        )
        self.delete_button.pack(side=Tkinter.RIGHT)

        self.log_display = LogDisplay(self)
        self.log_display.pack(fill=Tkinter.X)

    def deactivate_all_widgets(self):
        self.run_button.config(state=Tkinter.DISABLED)
        self.reset_button.config(state=Tkinter.DISABLED)
        self.delete_button.config(state=Tkinter.DISABLED)
        self.deploy_listbox.config(state=Tkinter.DISABLED)

    def activate_all_widgets(self):
        self.run_button.config(state=Tkinter.NORMAL)
        self.reset_button.config(state=Tkinter.NORMAL)
        self.delete_button.config(state=Tkinter.NORMAL)
        self.deploy_listbox.config(state=Tkinter.NORMAL)

    def refresh_deploy_list(self):
        self.deploy_listbox.delete(0, len(self.deploys)-1)
        self.deploys = []
        for deploy in db.Deploy.select():
            self.deploy_listbox.insert(Tkinter.END, deploy.resume())
            self.deploys.append(deploy.id)

    def selected_deploy(self):
        selected = self.deploy_listbox.curselection()
        if selected:
            idx = int(selected[0])
            return db.Deploy.get(id=self.deploys[idx])
        body = (
            "Please select a deploy"
            if self.deploys else
            "Please create and select a deploy"
        )
        tkMessageBox.showerror("No deploy selected", body)

    def do_delete(self):
        deploy = self.selected_deploy()
        msg = (
            "WARNING\nAre you sure to delete the deploy '{}'?\n"
            "(The files will not be removed)"
        )
        res = tkMessageBox.askokcancel(
            "Delete Deploy", msg.format(deploy.path)
        )
        if res:
            try:
                self.deactivate_all_widgets()
                deploy.delete_instance(True)
            except Exception as err:
                tkMessageBox.showerror("Something gone wrong", unicode(err))
            finally:
                self.activate_all_widgets()
                self.refresh_deploy_list()

    def do_clear(self):
        msg = (
            "WARNING:\n You are going to delete all the database?\n"
            "(The files will not be removed)"
        )
        res = tkMessageBox.askokcancel("Clear", msg)
        if res:
            db.clear_database()
            self.refresh_deploy_list()

    def do_reset(self):
        deploy = self.selected_deploy()
        res = tkMessageBox.askokcancel(
            "Reset Deploy",
            "Are you sure to reset the deploy '{}'?".format(deploy.path)
        )
        if res:
            try:
                self.deactivate_all_widgets()
                core.reset(deploy.path)
            except Exception as err:
                tkMessageBox.showerror("Something gone wrong", unicode(err))
            finally:
                self.activate_all_widgets()
                self.refresh_deploy_list()

    def do_run(self):
        deploy = self.selected_deploy()
        if deploy:
            proc = core.execute(deploy.path)
            core.open_webbrowser()
            msg = "The deploy '{}' is running\nStop the server?"
            tkMessageBox.showwarning("Deploy running", msg.format(deploy.path))
            core.kill_proc(proc)
            logger.info("Run Stop")

    def do_about(self):
        title = "About {} - v.{}".format(cons.PRJ, cons.STR_VERSION)
        body = (
            "{doc}"
            "A modern open platform for social science experiment\n"
            "Version: {version}"
        ).format(
            prj=cons.PRJ, url=cons.URL, doc=cons.DOC,
            version=cons.STR_VERSION
        )
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
                self.deactivate_all_widgets()
                proc = core.full_install_and_run(wrkpath)
                msg = "The deploy '{}' is running\nStop the server?"
                tkMessageBox.showwarning("Deploy running", msg.format(wrkpath))
                core.kill_proc(proc)
                logger.info("Run Stop")
            except Exception as err:
                tkMessageBox.showerror("Something gone wrong", unicode(err))
            finally:
                self.activate_all_widgets()
                self.refresh_deploy_list()


# =============================================================================
# FUNCTIONS
# =============================================================================

def run():
    # create gui
    root = Tkinter.Tk()

    with splash.Splash(root, res.get("splash.gif"), 1.9):
        root.geometry("900x600+50+50")
        root.title("{} - v.{}".format(cons.PRJ, cons.STR_VERSION))

        # set icon
        icon = Tkinter.PhotoImage(file=res.get("otree.gif"))
        root.tk.call('wm', 'iconphoto', root._w, icon)

        # add main frame
        frame = OTreeLauncherFrame(root)
        frame.pack(expand=True, fill=Tkinter.BOTH)

        # setup logger
        logger.handlers = []
        logger.addHandler(LoggingToGUI(frame.log_display.console))
        logger.info("oTree Launcher says 'Hello'")


    root.mainloop()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
