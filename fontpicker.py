from tkinter import Toplevel, Listbox, StringVar, BooleanVar, LabelFrame, TclError
from tkinter.ttk import Checkbutton, Frame, Label, Button, Scrollbar, Style, Entry
from tkinter.font import families, Font

import tkfontchooser  # file taken 11/4/2019


class FontChooser(tkfontchooser.FontChooser):
    def __init__(self, master, font_dict=None, text="AaBbYyZz", title="Font", **kwargs):

        Toplevel.__init__(self, master, **kwargs)
        self.title(title)

        try:
            self.wm_iconbitmap('transparent.ico')
        except TclError:
            pass

        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self._validate_family = self.register(self.validate_font_family)
        self._validate_size = self.register(self.validate_font_size)

        # --- variable storing the chosen font
        self.res = ""

        style = Style(self)
        style.configure("prev.TLabel")
        bg = style.lookup("TLabel", "background")
        self.configure(bg=bg)

        # --- family list
        self.fonts = list(set(families()))
        self.fonts.append("TkDefaultFont")
        self.fonts.sort()
        for i in range(len(self.fonts)):
            self.fonts[i] = self.fonts[i].replace(" ", "\ ")
        max_length = int(2.5 * max([len(font) for font in self.fonts])) // 3
        self.sizes = ["%i" % i for i in (list(range(6, 17)) + list(range(18, 32, 2)) + list(range(36, 48, 4)))]
        # --- font default
        font_dict["weight"] = font_dict.get("weight", "normal")
        font_dict["slant"] = font_dict.get("slant", "roman")
        font_dict["underline"] = font_dict.get("underline", False)
        font_dict["overstrike"] = font_dict.get("overstrike", False)
        font_dict["family"] = font_dict.get("family", self.fonts[0].replace('\ ', ' '))
        font_dict["size"] = font_dict.get("size", 10)

        # --- creation of the widgets
        options_frame = Frame(self, relief='groove')
        self.font_family = StringVar(self, " ".join(self.fonts))
        self.font_size = StringVar(self, " ".join(self.sizes))
        self.format_type = StringVar(self, " ".join(self.sizes))
        self.var_bold = BooleanVar(self, font_dict["weight"] == "bold")
        self.var_italic = BooleanVar(self, font_dict["slant"] == "italic")
        self.var_underline = BooleanVar(self, font_dict["underline"])

        # ------ Size and family
        self.var_size = StringVar(self)
        self.entry_family = Entry(self, width=max_length, validate="key",
                                  validatecommand=(self._validate_family, "%d", "%S",
                                                   "%i", "%s", "%V"))
        self.entry_size = Entry(self, width=4, validate="key",
                                textvariable=self.var_size,
                                validatecommand=(self._validate_size, "%d", "%P", "%V"))

        self.entry_format = Entry(self, width=8)

        self.list_family = Listbox(self, selectmode="browse",
                                   listvariable=self.font_family,
                                   highlightthickness=0,
                                   exportselection=False,
                                   width=max_length)
        self.list_size = Listbox(self, selectmode="browse",
                                 listvariable=self.font_size,
                                 highlightthickness=0,
                                 exportselection=False,
                                 width=4)
        self.format_box = Listbox(self, selectmode="browse",
                                  listvariable=self.font_size,
                                  highlightthickness=0,
                                  exportselection=False,
                                  width=8)
        scroll_family = Scrollbar(self, orient='vertical',
                                  command=self.list_family.yview)
        scroll_size = Scrollbar(self, orient='vertical',
                                command=self.list_size.yview)
        scroll_format = Scrollbar(self, orient='vertical',
                                command=self.format_box.yview)
        family_label = Label(self, text='Font:')
        style_label = Label(self, text='Font style:')
        size_label = Label(self, text='Size:')

        self.preview_font = Font(self, **font_dict)
        if len(text) > 30:
            text = text[:30]
        self.preview_window = LabelFrame(self, relief="groove", text='Sample', bd=1)

        # --- widget configuration
        self.list_family.configure(yscrollcommand=scroll_family.set)
        self.list_size.configure(yscrollcommand=scroll_size.set)

        self.entry_family.insert(0, font_dict["family"])
        self.entry_family.selection_clear()
        self.entry_family.icursor("end")
        self.entry_size.insert(0, font_dict["size"])

        try:
            i = self.fonts.index(self.entry_family.get().replace(" ", "\ "))
        except ValueError:
            # unknown font
            i = 0
        self.list_family.selection_clear(0, "end")
        self.list_family.selection_set(i)
        self.list_family.see(i)
        try:
            i = self.sizes.index(self.entry_size.get())
            self.list_size.selection_clear(0, "end")
            self.list_size.selection_set(i)
            self.list_size.see(i)
        except ValueError:
            # size not in list
            pass

        family_label.grid(row=0, column=0, sticky='nsew', padx=(15, 1), pady=(10, 1))
        self.entry_family.grid(row=1, column=0, sticky="nsew", pady=(1, 1), padx=(15, 0), columnspan=2)
        self.list_family.grid(row=2, column=0, sticky="nsew", pady=(1, 10), padx=(15, 0))
        scroll_family.grid(row=2, column=1, sticky='ns', pady=(1, 10))

        style_label.grid(row=0, column=2, sticky='nsew', padx=(20, 1), pady=(10, 1))
        self.entry_family.grid(row=1, column=2, sticky="nsew", pady=(1, 1), padx=(15, 0), columnspan=2)
        self.format_box.grid(row=2, column=2, sticky="nsew", pady=(1, 10), padx=(15, 0))

        size_label.grid(row=0, column=3, sticky='nsew', padx=(20, 1), pady=(10, 1))
        self.entry_size.grid(row=1, column=3, sticky="nsew", pady=(1, 1), padx=(20, 15), columnspan=2)

        self.list_size.grid(row=2, column=3, sticky="ns", pady=(1, 10), padx=(20, 0))
        scroll_size.grid(row=2, column=4, sticky='ns', pady=(1, 10), padx=(1, 15))

        self.preview_window.grid(row=4, column=0, columnspan=5, sticky="nsew", rowspan=2, padx=15, pady=(0, 10),
                                 ipadx=10, ipady=10)

        self.preview_window.config(height=75)
        preview = Label(self.preview_window, text=text, font=self.preview_font, anchor="center")
        preview.place(relx=0.5, rely=0.5, anchor="center")

        button_frame = Frame(self)
        button_frame.grid(row=6, column=2, columnspan=3, pady=(0, 10), padx=10)

        Button(button_frame, text="Ok", command=self.ok).grid(row=0, column=0, padx=4, sticky='ew')
        Button(button_frame, text="Cancel", command=self.quit).grid(row=0, column=1, padx=4, sticky='ew')

        self.list_family.bind('<<ListboxSelect>>', self.update_entry_family)
        self.list_size.bind('<<ListboxSelect>>', self.update_entry_size, add=True)
        self.list_family.bind("<KeyPress>", self.keypress)
        self.entry_family.bind("<Return>", self.change_font_family)
        self.entry_family.bind("<Tab>", self.tab)
        self.entry_size.bind("<Return>", self.change_font_size)

        self.entry_family.bind("<Down>", self.down_family)
        self.entry_size.bind("<Down>", self.down_size)
        self.entry_family.bind("<Up>", self.up_family)
        self.entry_size.bind("<Up>", self.up_size)

        # bind Ctrl+A to select all instead of go to beginning
        self.bind_class("TEntry", "<Control-a>", self.select_all)

        self.wait_visibility(self)
        self.grab_set()
        self.entry_family.focus_set()
        self.lift()


def ask_font(master=None, text="AaBbYyZz", title="Font", **font_args):
    chooser = FontChooser(master, font_args, text, title)
    chooser.wait_window(chooser)
    return chooser.get_res()