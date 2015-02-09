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

from . import cons, core, res, ctx
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
        self.conf = core.get_conf()

        # icons
        self.icon_new = Tkinter.PhotoImage(file=res.get("new.gif"))
        self.icon_exit = Tkinter.PhotoImage(file=res.get("exit.gif"))
        self.icon_homepage = Tkinter.PhotoImage(file=res.get("homepage.gif"))
        self.icon_about = Tkinter.PhotoImage(file=res.get("about.gif"))

        self.icon_run = Tkinter.PhotoImage(file=res.get("run.gif"))
        self.icon_opendir = Tkinter.PhotoImage(file=res.get("opendir.gif"))
        self.icon_clear = Tkinter.PhotoImage(file=res.get("clear.gif"))
        self.icon_stop = Tkinter.PhotoImage(file=res.get("stop.gif"))

        # =====================================================================
        # MENU
        # =====================================================================

        self.menu = Tkinter.Menu(self)
        root.config(menu=self.menu)

        self.deploy_menu = Tkinter.Menu(self.menu)
        self.deploy_menu.add_command(
            label="New Deploy", command=self.do_deploy,
            compound=Tkinter.LEFT, image=self.icon_new
        )
        self.deploy_menu.add_separator()
        self.deploy_menu.add_command(
            label="Exit", command=self.do_exit,
            compound=Tkinter.LEFT, image=self.icon_exit
        )
        self.menu.add_cascade(label="Deploys", menu=self.deploy_menu)

        self.about_menu = Tkinter.Menu(self.menu)
        self.about_menu.add_command(
            label="oTree Homepage", command=self.do_open_homepage,
            compound=Tkinter.LEFT, image=self.icon_homepage
        )
        self.about_menu.add_command(
            label="About oTree Launcher", command=self.do_about,
            compound=Tkinter.LEFT, image=self.icon_about
        )
        self.menu.add_cascade(label="About", menu=self.about_menu)

        # =====================================================================
        # DIRECTORY COMBO
        # =====================================================================
        directory_opts = {"side": Tkinter.LEFT, "padx": 5, "pady": 5}

        directory_frame = ttk.LabelFrame(self, text="Project Directory")
        directory_frame.pack(fill=Tkinter.X)

        self.deploy_path = Tkinter.StringVar()
        self.deploy_entry = ttk.Entry(
            directory_frame, textvariable=self.deploy_path,
            state=["readonly"]
        )
        self.deploy_entry.pack(
            fill=Tkinter.X, expand=True, **directory_opts
        )

        self.opendirectory_button = ttk.Button(
            directory_frame, text="", command=self.do_opendir,
            compound=Tkinter.LEFT, image=self.icon_opendir
        )
        self.opendirectory_button.pack(**directory_opts)

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

        self.refresh_deploy_path()

    def setup_env(self):
        if self.conf.virtualenv:
            return

        def clean():
            self.conf.virtualenv = True
            self.conf.save()
            self.refresh_deploy_path()
            tkMessageBox.showinfo(
                "First run setup",
                ("Initial setup complete.\n"
                 "Click on the 'Deploys' menu to create a new deploy.")
            )

        msg = (
            "This is your first time running the oTree launcher.\n"
            "Initial setup may take a few minutes.\n"
        )
        tkMessageBox.showinfo("First run setup", msg)
        self.proc = core.create_virtualenv()

        self.check_proc_end(clean, setup_complete_msg)

    def refresh_deploy_path(self):

        if self.conf.path and not os.path.isdir(self.conf.path):
            self.conf.path = None
            self.conf.save()

        self.deploy_path.set(self.conf.path or "")
        state = Tkinter.NORMAL if self.conf.path else Tkinter.DISABLED
        self.run_button.config(state=state)
        self.clear_button.config(state=state)

        state = Tkinter.NORMAL if self.conf.virtualenv else Tkinter.DISABLED
        self.deploy_menu.entryconfig(1, state=state)
        self.opendirectory_button.config(state=state)

    def check_proc_end(self, cleaner, msg):
        if self.proc and self.proc.poll() is None:
            self.root.after(1000, self.check_proc_end, cleaner, msg)
        else:
            self.proc = None
            cleaner()
            logger.info(msg)

    # =========================================================================
    # SLOTS
    # =========================================================================

    def do_clear(self):
        msg = (
            "Are you sure to you want to clear the"
            "database for the deploy '{}'?"
        ).format(self.conf.path)
        res = tkMessageBox.askokcancel("Reset Deploy", msg)
        if res:

            def clean():
                self.run_button.config(state=Tkinter.NORMAL)
                self.clear_button.config(state=Tkinter.NORMAL)
                self.opendirectory_button.config(state=Tkinter.NORMAL)
                self.deploy_menu.entryconfig(1, state=Tkinter.NORMAL)

            try:
                self.run_button.config(state=Tkinter.DISABLED)
                self.clear_button.config(state=Tkinter.DISABLED)
                self.opendirectory_button.config(state=Tkinter.DISABLED)
                self.deploy_menu.entryconfig(1, state=Tkinter.DISABLED)
                self.proc = core.reset_db(self.conf.path)
                self.check_proc_end(clean, "Database Reset done")
            except Exception as err:
                tkMessageBox.showerror("Something gone wrong", unicode(err))
                clean()

    def do_run(self):
        try:
            self.run_button.config(state=Tkinter.DISABLED)
            self.clear_button.config(state=Tkinter.DISABLED)
            self.opendirectory_button.config(state=Tkinter.DISABLED)
            self.deploy_menu.entryconfig(1, state=Tkinter.DISABLED)
            self.proc = core.runserver(self.conf.path)
        except:
            self.run_button.config(state=Tkinter.NORMAL)
            self.clear_button.config(state=Tkinter.NORMAL)
            self.opendirectory_button.config(state=Tkinter.NORMAL)
            self.deploy_menu.entryconfig(1, state=Tkinter.NORMAL)
            self.stop_button.config(state=Tkinter.DISABLED)
            tkMessageBox.showerror("Something gone wrong", unicode(err))
        else:
            core.open_webbrowser()
            self.stop_button.config(state=Tkinter.NORMAL)

    def do_stop(self):
        if self.proc:
            logger.info("Killing process...")
            if self.proc.poll() is None:
                core.kill_proc(self.proc)
            self.proc = None
        self.run_button.config(state=Tkinter.NORMAL)
        self.clear_button.config(state=Tkinter.NORMAL)
        self.opendirectory_button.config(state=Tkinter.NORMAL)
        self.deploy_menu.entryconfig(1, state=Tkinter.NORMAL)
        self.stop_button.config(state=Tkinter.DISABLED)

    def do_about(self):
        title = "About {} - v.{}".format(cons.PRJ, cons.STR_VERSION)
        body = (
            "{doc}\n"
            "A modern open platform for social science experiments\n"
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

    def do_opendir(self):
        options = {
            'parent': self,
            'initialdir': self.conf.path or cons.HOME_DIR,
            'mustexist': True,
            'title': 'Select oTree directory'
        }
        dpath = tkFileDialog.askdirectory(**options)
        if dpath:
            self.conf.path = dpath
            self.conf.save()
            self.refresh_deploy_path()

    def do_deploy(self):
        # define options for opening or saving a file
        options = {
            'parent': self,
            'initialdir': cons.HOME_DIR,
            'mustexist': False,
            'title': 'Select an empty folder for your oTree project files.'
        }
        wrkpath = None
        while True:
            dpath = tkFileDialog.askdirectory(**options)
            if not dpath:
                return None
            if os.path.isdir(dpath) and len(os.listdir(dpath)):
                options["initialdir"] = dpath
                msg = "Please select an empty directory"
                tkMessageBox.showwarning("Directory is not empty", msg)
            else:
                wrkpath = dpath
                break
        if wrkpath:
            try:

                def block():
                    self.run_button.config(state=Tkinter.DISABLED)
                    self.clear_button.config(state=Tkinter.DISABLED)
                    self.opendirectory_button.config(state=Tkinter.DISABLED)
                    self.deploy_menu.entryconfig(1, state=Tkinter.DISABLED)

                def clean():
                    self.run_button.config(state=Tkinter.NORMAL)
                    self.clear_button.config(state=Tkinter.NORMAL)
                    self.opendirectory_button.config(state=Tkinter.NORMAL)
                    self.deploy_menu.entryconfig(1, state=Tkinter.NORMAL)
                    self.refresh_deploy_path()

                def setdir():
                    block()
                    self.conf.path = wrkpath
                    self.conf.save()
                    clean()

                def reset():
                    block()
                    self.proc = core.reset_db(wrkpath)
                    self.check_proc_end(
                        setdir,
                        ("Deploy done. Click the 'Run' button to start the "
                         "server. Or, you can first modify the apps in your "
                         "project directory.")
                    )

                def install():
                    block()
                    self.proc = core.install_requirements(wrkpath)
                    self.check_proc_end(reset, "Install done")

                block()
                self.proc = core.clone(wrkpath)
                self.check_proc_end(install, "Clone done")
            except Exception as err:
                tkMessageBox.showerror("Something went wrong", unicode(err))
                clean()


# =============================================================================
# FUNCTIONS
# =============================================================================


def run():
    # create gui
    root = Tkinter.Tk()

    with splash.Splash(root, res.get("splash.gif"), 1):

        core.clean_tempdir()
        fp = core.logfile_fp()

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

        logger.info("The oTree Launcher says 'Hello'")

    def read_log_file():
        line = fp.readline()
        if line:
            logger.info(line.rstrip())
        root.after(10, read_log_file)

    read_log_file()

    frame.setup_env()

    root.mainloop()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
