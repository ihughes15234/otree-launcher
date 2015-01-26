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
import ttk

from . import cons, core, db, res
from .libs import splash


# =============================================================================
# LOGGER
# =============================================================================

logger = cons.logger


# =============================================================================
# LOGGER UI
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

class LogDisplay(ttk.LabelFrame):
    """A simple 'console' to place at the bottom of a Tkinter window """

    def __init__(self, root, **options):
        ttk.LabelFrame.__init__(self, root, **options)
        self.console = Tkinter.Text(self, height=10)
        self.console.configure(state=Tkinter.DISABLED)
        self.console.configure(bg="#222222", fg="#dddddd")
        self.console.pack(fill=Tkinter.BOTH, expand=True)


class OTreeLauncherFrame(ttk.Frame):

    def __init__(self, root):
        ttk.Frame.__init__(self, root)
        self.root = root
        self.proc = None

        # icons
        self.icon_new = Tkinter.PhotoImage(file=res.get("new.gif"))
        self.icon_exit = Tkinter.PhotoImage(file=res.get("exit.gif"))
        self.icon_homepage = Tkinter.PhotoImage(file=res.get("homepage.gif"))
        self.icon_about = Tkinter.PhotoImage(file=res.get("about.gif"))

        self.icon_run = Tkinter.PhotoImage(file=res.get("run.gif"))
        self.icon_delete = Tkinter.PhotoImage(file=res.get("delete.gif"))
        self.icon_clear = Tkinter.PhotoImage(file=res.get("clear.gif"))
        self.icon_stop = Tkinter.PhotoImage(file=res.get("stop.gif"))

        # =====================================================================
        # MENU
        # =====================================================================

        self.menu = Tkinter.Menu(self)
        root.config(menu=self.menu)

        deploy_menu = Tkinter.Menu(self.menu)
        deploy_menu.add_command(
            label="New Deploy", command=self.do_deploy,
            compound=Tkinter.LEFT, image=self.icon_new
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

        # =====================================================================
        # DIRECTORY COMBO
        # =====================================================================
        directory_frame = ttk.LabelFrame(self, text="Project Directory")
        directory_frame.pack(fill=Tkinter.X)

        self.selected_deploy = Tkinter.StringVar()
        self.deploys_combobox = ttk.Combobox(
            directory_frame, textvariable=self.selected_deploy,
            state=["readonly"]
        )
        self.deploys_combobox.bind(
            "<<ComboboxSelected>>", self.do_select_deploy
        )
        self.deploys_combobox.pack(fill=Tkinter.X, padx=5, pady=5)
        self.refresh_deploy_list()
        self.delete_button = ttk.Button(
            directory_frame, text="", command=self.do_delete,
            compound=Tkinter.LEFT, image=self.icon_delete
        )
        button_opt = {'side': Tkinter.LEFT, 'padx': 5, 'pady': 5}
        self.run_button.pack(**button_opt)



        # =====================================================================
        # BUTTONS
        # =====================================================================

        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=Tkinter.X)
        button_opt = {'side': Tkinter.LEFT, 'padx': 5, 'pady': 5}

        self.run_button = ttk.Button(
            buttons_frame, text="Run", command=self.do_run,
            compound=Tkinter.LEFT, image=self.icon_run
        )
        self.run_button.pack(**button_opt)

        self.stop_button = ttk.Button(
            buttons_frame, text="Stop", command=self.do_stop,
            compound=Tkinter.LEFT, image=self.icon_stop
        )
        self.stop_button.config(state=Tkinter.DISABLED)
        self.stop_button.pack(**button_opt)

        self.clear_button = ttk.Button(
            buttons_frame, text="Clear Database", command=self.do_clear,
            compound=Tkinter.LEFT, image=self.icon_clear
        )
        self.clear_button.pack(**button_opt)


        # =====================================================================
        # CONSOLE
        # =====================================================================
        self.log_display = LogDisplay(self, text="Console")
        self.log_display.pack(fill=Tkinter.BOTH, expand=True)

    def refresh_deploy_list(self):
        combo_values = []
        for deploy in db.Deploy.select():
            combo_values.append(deploy.path)
            if deploy.selected:
                self.selected_deploy.set(deploy.path)
        self.deploys_combobox["values"] = combo_values

    # =========================================================================
    # SLOTS
    # =========================================================================

    def do_select_deploy(self, e=None):
        path = self.deploys_combobox.get()
        deploy = db.Deploy.select().where(db.Deploy.path == path).get()
        deploy.selected = True
        deploy.save()

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
        deploy = db.Deploy.select().where(db.Deploy.selected == True).get()
        msg = "Are you sure to clear the database of the deploy '{}'?"
        res = tkMessageBox.askokcancel("Reset Deploy", msg.format(deploy.path))
        if res:
            try:
                self.run_button.config(state=Tkinter.DISABLED)
                self.clear_button.config(state=Tkinter.DISABLED)
                self.deploys_combobox.config(state=Tkinter.DISABLED)
                core.reset(deploy.path)
                logger.info("Reset done!")
            except Exception as err:
                tkMessageBox.showerror("Something gone wrong", unicode(err))
            finally:
                self.run_button.config(state=Tkinter.NORMAL)
                self.clear_button.config(state=Tkinter.NORMAL)
                self.deploys_combobox.config(state="readonly")

    def do_run(self):
        deploy = db.Deploy.select().where(db.Deploy.selected == True).get()
        try:
            self.run_button.config(state=Tkinter.DISABLED)
            self.clear_button.config(state=Tkinter.DISABLED)
            self.deploys_combobox.config(state=Tkinter.DISABLED)
            self.proc = core.execute(deploy.path)
        except:
            self.run_button.config(state=Tkinter.NORMAL)
            self.clear_button.config(state=Tkinter.NORMAL)
            self.deploys_combobox.config(state="readonly")
            self.stop_button.config(state=Tkinter.DISABLED)
            tkMessageBox.showerror("Something gone wrong", unicode(err))
        else:
            core.open_webbrowser()
            self.stop_button.config(state=Tkinter.NORMAL)

    def do_stop(self):
        if self.proc:
            logger.info("Killing process...")
            core.kill_proc(self.proc)
            self.proc = None
        self.run_button.config(state=Tkinter.NORMAL)
        self.clear_button.config(state=Tkinter.NORMAL)
        self.deploys_combobox.config(state="readonly")
        self.stop_button.config(state=Tkinter.DISABLED)

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
                self.run_button.config(state=Tkinter.DISABLED)
                self.clear_button.config(state=Tkinter.DISABLED)
                self.deploys_combobox.config(state=Tkinter.DISABLED)
                core.download(wrkpath)
                core.install(wrkpath)
                core.reset(wrkpath)
                logger.info("Deploy finished")
            except Exception as err:
                tkMessageBox.showerror("Something gone wrong", unicode(err))
            finally:
                self.run_button.config(state=Tkinter.NORMAL)
                self.clear_button.config(state=Tkinter.NORMAL)
                self.deploys_combobox.config(state="readonly")
                self.refresh_deploy_list()


# =============================================================================
# FUNCTIONS
# =============================================================================

def run():
    # create gui
    root = Tkinter.Tk()

    with splash.Splash(root, res.get("splash.gif"), 1.9):
        root.geometry("500x530+50+50")
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
