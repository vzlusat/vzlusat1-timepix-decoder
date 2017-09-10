import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
    import tkFileDialog
    import ttk
    import tkFont
else:
    import tkinter as Tk
    import tkinter.filedialog
    from tkinter import ttk
    import tkinter.font as tkFont

def init(root, customfont):

    global v
    global root_

    v = Tk.StringVar()
    root_ = root

    status_line = Tk.Label(root, anchor=Tk.W, justify=Tk.LEFT, textvariable=v, height=1, bg="white", bd=2, highlightbackground="black", font=customfont)
    status_line.pack(side=Tk.BOTTOM, fill=Tk.X, expand=0)

def set(text):

    v.set(text)
    root_.update()
