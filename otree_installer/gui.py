import Tkinter, Tkconstants, tkFileDialog

from . import cons, core


def ask_directory(parent):
    # define options for opening or saving a file
    options = {
        'parent': parent,
        'initialdir': cons.HOME_DIR,
        'mustexist': True,
        'title': 'Select directory for install oTree'
    }
    while True:
        dpath = tkFileDialog.askdirectory(**options)
        if dpath is None:
            return None
        elif len(dpath):
            msg = "Please select an empty directory"
            print msg
        else:
            return dpath

def run():
    root = Tkinter.Tk()
    root.withdraw()

    wrkpath = ask_directory(root)
    if wrkpath:
        pass

    root.destroy()
    root.mainloop()


if __name__=='__main__':
  run()
