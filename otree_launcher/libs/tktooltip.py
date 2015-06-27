#!/usr/bin/env python
# -*- coding: utf-8 -*-

# http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml

from Tkinter import *


class ToolTip(object):

    def __init__(self, widget, text, disable_text=None):
        self.widget = widget
        self.text = text
        self.disable_text = disable_text or text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

        # bind
        widget.bind('<Enter>', self.showtip)
        widget.bind('<Leave>', self.hidetip)


    def showtip(self, event=None):
        "Display text in tooltip window"
        disabled = (self.widget.cget("state").string == DISABLED)
        text = self.disable_text if disabled else self.text
        if self.tipwindow or not text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass
        label = Label(tw, text=text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
