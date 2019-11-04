from tkinter import Toplevel, Listbox, StringVar, BooleanVar, TclError, LabelFrame
from tkinter.ttk import Checkbutton, Frame, Label, Button, Scrollbar, Style, Entry
from tkinter.font import families, Font


class FontChooser(Toplevel):
    def __init__(self, master, font_dict=None, text="AaBbYyZz", title="Font", **kwargs):

        Toplevel.__init__(self, master, **kwargs)
        self.title(title)
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
        # ------ style parameters (bold, italic ...)
        options_frame = Frame(self, relief='groove')
        self.font_family = StringVar(self, " ".join(self.fonts))
        self.font_size = StringVar(self, " ".join(self.sizes))
        self.var_bold = BooleanVar(self, font_dict["weight"] == "bold")
        b_bold = Checkbutton(options_frame, text="Bold",
                             command=self.toggle_bold,
                             variable=self.var_bold)
        b_bold.grid(row=0, sticky="w", padx=4, pady=(4, 2))
        self.var_italic = BooleanVar(self, font_dict["slant"] == "italic")
        b_italic = Checkbutton(options_frame, text="Italic",
                               command=self.toggle_italic,
                               variable=self.var_italic)
        b_italic.grid(row=1, sticky="w", padx=4, pady=2)
        self.var_underline = BooleanVar(self, font_dict["underline"])
        b_underline = Checkbutton(options_frame, text="Underline",
                                  command=self.toggle_underline,
                                  variable=self.var_underline)
        b_underline.grid(row=2, sticky="w", padx=4, pady=2)
        self.var_overstrike = BooleanVar(self, font_dict["overstrike"])
        b_overstrike = Checkbutton(options_frame, text="Strikethrough",
                                   variable=self.var_overstrike,
                                   command=self.toggle_overstrike)
        b_overstrike.grid(row=3, sticky="w", padx=4, pady=(2, 4))

        # ------ Size and family
        self.var_size = StringVar(self)
        self.entry_family = Entry(self, width=max_length, validate="key",
                                  validatecommand=(self._validate_family, "%d", "%S",
                                                   "%i", "%s", "%V"))
        self.entry_size = Entry(self, width=4, validate="key",
                                textvariable=self.var_size,
                                validatecommand=(self._validate_size, "%d", "%P", "%V"))
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
        scroll_family = Scrollbar(self, orient='vertical',
                                  command=self.list_family.yview)
        scroll_size = Scrollbar(self, orient='vertical',
                                command=self.list_size.yview)
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
        options_frame.grid(row=1, column=2, rowspan=2, padx=(20, 1), pady=(1, 10), sticky='new')

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

    def select_all(self, event):
        event.widget.selection_range(0, "end")

    def keypress(self, event):
        """Select the first font whose name begin by the key pressed."""
        key = event.char.lower()
        l = [i for i in self.fonts if i[0].lower() == key]
        if l:
            i = self.fonts.index(l[0])
            self.list_family.selection_clear(0, "end")
            self.list_family.selection_set(i)
            self.list_family.see(i)
            self.update_entry_family()

    def up_family(self, event):
        """Navigate in the family listbox with up key."""
        try:
            i = self.list_family.curselection()[0]
            self.list_family.selection_clear(0, "end")
            if i <= 0:
                i = len(self.fonts)
            self.list_family.see(i - 1)
            self.list_family.select_set(i - 1)
        except TclError:
            self.list_family.selection_clear(0, "end")
            i = len(self.fonts)
            self.list_family.see(i - 1)
            self.list_family.select_set(i - 1)
        self.list_family.event_generate('<<ListboxSelect>>')

    def up_size(self, event):
        """Navigate in the size listbox with up key."""
        try:
            s = self.var_size.get()
            if s in self.sizes:
                i = self.sizes.index(s)
            elif s:
                sizes = list(self.sizes)
                sizes.append(s)
                sizes.sort(key=lambda x: int(x))
                i = sizes.index(s)
            else:
                i = 0
            self.list_size.selection_clear(0, "end")
            if i <= 0:
                i = len(self.sizes)
            self.list_size.see(i - 1)
            self.list_size.select_set(i - 1)
        except TclError:
            i = len(self.sizes)
            self.list_size.see(i - 1)
            self.list_size.select_set(i - 1)
        self.list_size.event_generate('<<ListboxSelect>>')

    def down_family(self, event):
        """Navigate in the family listbox with down key."""
        try:
            i = self.list_family.curselection()[0]
            self.list_family.selection_clear(0, "end")
            if i >= len(self.fonts):
                i = -1
            self.list_family.see(i + 1)
            self.list_family.select_set(i + 1)
        except TclError:
            self.list_family.selection_clear(0, "end")
            self.list_family.see(0)
            self.list_family.select_set(0)
        self.list_family.event_generate('<<ListboxSelect>>')

    def down_size(self, event):
        """Navigate in the size listbox with down key."""
        try:
            i = 0
            s = self.var_size.get()
            if s in self.sizes:
                i = self.sizes.index(s)
            elif s:
                sizes = list(self.sizes)
                sizes.append(s)
                sizes.sort(key=lambda x: int(x))
                i = sizes.index(s) - 1
            else:
                s = len(self.sizes) - 1
            self.list_size.selection_clear(0, "end")
            if i < len(self.sizes) - 1:
                self.list_size.selection_set(i + 1)
                self.list_size.see(i + 1)
            else:
                self.list_size.see(0)
                self.list_size.select_set(0)
        except TclError:
            self.list_size.selection_set(0)
        self.list_size.event_generate('<<ListboxSelect>>')

    def toggle_bold(self):
        """Update font preview weight."""
        b = self.var_bold.get()
        self.preview_font.configure(weight=["normal", "bold"][b])

    def toggle_italic(self):
        """Update font preview slant."""
        b = self.var_italic.get()
        self.preview_font.configure(slant=["roman", "italic"][b])

    def toggle_underline(self):
        """Update font preview underline."""
        b = self.var_underline.get()
        self.preview_font.configure(underline=b)

    def toggle_overstrike(self):
        """Update font preview overstrike."""
        b = self.var_overstrike.get()
        self.preview_font.configure(overstrike=b)

    def change_font_family(self, event=None):
        """Update font preview family."""
        family = self.entry_family.get()
        if family.replace(" ", "\ ") in self.fonts:
            self.preview_font.configure(family=family)

    def change_font_size(self, event=None):
        """Update font preview size."""
        size = int(self.var_size.get())
        self.preview_font.configure(size=size)

    def validate_font_size(self, d, ch, V):
        """Validation of the size entry content."""
        l = [i for i in self.sizes if i[:len(ch)] == ch]
        i = None
        if l:
            i = self.sizes.index(l[0])
        elif ch.isdigit():
            sizes = list(self.sizes)
            sizes.append(ch)
            sizes.sort(key=lambda x: int(x))
            i = min(sizes.index(ch), len(self.sizes))
        if i is not None:
            self.list_size.selection_clear(0, "end")
            self.list_size.selection_set(i)
            deb = self.list_size.nearest(0)
            fin = self.list_size.nearest(self.list_size.winfo_height())
            if V != "forced":
                if i < deb or i > fin:
                    self.list_size.see(i)
                return True
        if d == '1':
            return ch.isdigit()
        else:
            return True

    def tab(self, event):
        """Move at the end of selected text on tab press."""
        self.entry_family = event.widget
        self.entry_family.selection_clear()
        self.entry_family.icursor("end")
        return "break"

    def validate_font_family(self, action, modif, pos, prev_txt, V):
        """Completion of the text in the entry with existing font names."""
        if self.entry_family.selection_present():
            sel = self.entry_family.selection_get()
            txt = prev_txt.replace(sel, '')
        else:
            txt = prev_txt
        if action == "0":
            txt = txt[:int(pos)] + txt[int(pos) + 1:]
            return True
        else:
            txt = txt[:int(pos)] + modif + txt[int(pos):]
            ch = txt.replace(" ", "\ ")
            l = [i for i in self.fonts if i[:len(ch)] == ch]
            if l:
                i = self.fonts.index(l[0])
                self.list_family.selection_clear(0, "end")
                self.list_family.selection_set(i)
                deb = self.list_family.nearest(0)
                fin = self.list_family.nearest(self.list_family.winfo_height())
                index = self.entry_family.index("insert")
                self.entry_family.delete(0, "end")
                self.entry_family.insert(0, l[0].replace("\ ", " "))
                self.entry_family.selection_range(index + 1, "end")
                self.entry_family.icursor(index + 1)
                if V != "forced":
                    if i < deb or i > fin:
                        self.list_family.see(i)
                return True
            else:
                return False

    def update_entry_family(self, event=None):
        """Update family entry when an item is selected in the family listbox."""
        #  family = self.list_family.get("@%i,%i" % (event.x , event.y))
        family = self.list_family.get(self.list_family.curselection()[0])
        self.entry_family.delete(0, "end")
        self.entry_family.insert(0, family)
        self.entry_family.selection_clear()
        self.entry_family.icursor("end")
        self.change_font_family()

    def update_entry_size(self, event):
        """Update size entry when an item is selected in the size listbox."""
        #  size = self.list_size.get("@%i,%i" % (event.x , event.y))
        size = self.list_size.get(self.list_size.curselection()[0])
        self.var_size.set(size)
        self.change_font_size()

    def ok(self):
        """Validate choice."""
        self.res = self.preview_font.actual()
        self.quit()

    def get_res(self):
        """Return chosen font."""
        return self.res

    def quit(self):
        self.destroy()


def ask_font(master=None, text="AaBbYyZz", title="Font", **font_args):
    """
    Open the font chooser and return a dictionary of the font properties.
    General Arguments:
        master : Tk or Toplevel instance
            master window
        text : str
            sample text to be displayed in the font chooser
        title : str
            dialog title

    Font arguments:
        family : str
            font family
        size : int
            font size
        slant : str
            "roman" or "italic"
        weight : str
            "normal" or "bold"
        underline : bool
            whether the text is underlined
        overstrike : bool
            whether the text is overstriked

    Output:
        dictionary is similar to the one returned by the ``actual`` method of a tkinter ``Font`` object:
        ::
            {'family': str,
             'size': int,
             'weight': 'bold'/'normal',
             'slant': 'italic'/'roman',
             'underline': bool,
             'overstrike': bool}

    """
    chooser = FontChooser(master, font_args, text, title)
    chooser.wait_window(chooser)
    return chooser.get_res()
