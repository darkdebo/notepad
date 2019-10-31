from tkinter import Toplevel, LabelFrame
from tkinter.ttk import Checkbutton, Frame, Label, Button, Radiobutton, Entry


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return get_instance


@singleton
class FindWindow(Toplevel):
    def __init__(self, master, **kwargs):
        Toplevel.__init__(self, master, **kwargs)

        self.title('Find')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit)

        # search string box
        self.find_label = Label(self, text='Find what:')
        self.find_label.grid(row=1, column=1, sticky='new', pady=(12, 10), padx=(5, 10))
        self.entry_find = Entry(self, width=25)
        self.entry_find.grid(row=1, column=2, columnspan=2, sticky='new', padx=(0, 0), pady=(10, 10))

        # find next, cancel buttons
        self.button_frame = Frame(self)
        self.button_frame.grid(row=1, column=4, rowspan=2, pady=(10, 0), padx=(10, 5), sticky='ne')
        Button(self.button_frame, text="Find next",
               command=self.quit).grid(row=0, column=0, padx=5, pady=(0, 0), sticky='ew')
        Button(self.button_frame, text="Cancel",
               command=self.quit).grid(row=1, column=0, padx=5, pady=(5, 0), sticky='ew')

        # match case checkbox
        self.match_case = Checkbutton(self, text='Match case')
        self.match_case.grid(row=2, column=1, sticky="sw", padx=5, pady=10, columnspan=2)

        # directional radiobutton
        self.direction_box = LabelFrame(self, text='Direction')
        self.direction_box.grid(row=2, column=3, sticky='ne', pady=(0, 10))
        self.up_button = Radiobutton(self.direction_box, text='Up')
        self.up_button.grid(row=1, column=1, padx=5)
        self.down_button = Radiobutton(self.direction_box, text='Down')
        self.down_button.grid(row=1, column=2, padx=(0, 5))

    def quit(self):
        self.destroy()


@singleton
class FindReplaceWindow(Toplevel):
    def __init__(self, master, **kwargs):
        Toplevel.__init__(self, master, **kwargs)

        self.title('Replace')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit)

        # search string box
        self.find_label = Label(self, text='Find what:')
        self.find_label.grid(row=1, column=1, sticky='new', pady=(12, 10), padx=(5, 10))
        self.entry_find = Entry(self, width=25)
        self.entry_find.grid(row=1, column=2, columnspan=2, sticky='new', padx=(0, 0), pady=(10, 10))

        # replace string box
        self.replace_label = Label(self, text='Replace:')
        self.replace_label.grid(row=2, column=1, sticky='new', pady=(11, 10), padx=(5, 10))
        self.entry_replace = Entry(self, width=25)
        self.entry_replace.grid(row=2, column=2, columnspan=2, sticky='new', padx=(0, 0), pady=(10, 10))

        # buttons
        self.button_frame = Frame(self)
        self.button_frame.grid(row=1, column=4, rowspan=4, pady=(10, 0), padx=(10, 5), sticky='ne')
        Button(self.button_frame, text="Find next",
               command=self.quit).grid(row=0, column=0, padx=5, pady=(0, 5), sticky='new')
        Button(self.button_frame, text="Cancel",
               command=self.quit).grid(row=1, column=0, padx=5, pady=(0, 5), sticky='new')
        Button(self.button_frame, text="Replace",
               command=self.quit).grid(row=2, column=0, padx=5, pady=(0, 5), sticky='new')
        Button(self.button_frame, text="Replace all",
               command=self.quit).grid(row=3, column=0, padx=5, pady=(0, 5), sticky='new')

        # match case checkbox
        self.match_case = Checkbutton(self, text='Match case')
        self.match_case.grid(row=3, column=1, sticky="sw", padx=5, pady=0, columnspan=2)
        self.match_whole_word = Checkbutton(self, text='Match whole word only')
        self.match_whole_word.grid(row=4, column=1, sticky="sw", padx=5, pady=10, columnspan=2)


    def quit(self):
        self.destroy()


