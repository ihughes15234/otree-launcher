
import os

import Tkinter, Tkconstants, tkMessageBox, tkFileDialog

from . import cons, core


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
        if dpath is None:
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
    root.withdraw()

    wrkpath = ask_directory(root)
    if wrkpath:
        core.full_install_and_run(wrkpath)

    root.destroy()
    root.mainloop()


if __name__=='__main__':
  run()
