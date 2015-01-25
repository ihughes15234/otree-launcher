from Tkinter import *
import ttk

master = Tk()

variable = StringVar(master)
variable.set("one") # default value

w = ttk.OptionMenu(master, variable, "one", "two", "three")
w.pack()

mainloop()
