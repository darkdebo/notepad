import logging as log
import webbrowser
from tkinter import Label as Lbl
from tkinter import Toplevel, Listbox, StringVar, BooleanVar, LabelFrame, TclError, TRUE, FALSE
from tkinter.font import families, Font
from tkinter.ttk import Frame, Label, Button, Scrollbar, Style, Entry, Combobox

import tkfontchooser  # file taken 11/4/2019


class FontChooser(tkfontchooser.FontChooser):
    def __init__(self, master, font_dict=None, text='AaBbYyZz', title='Font', **kwargs):

        Toplevel.__init__(self, master, **kwargs)
        self.title(title)

        try:
            self.wm_iconbitmap('transparent.ico')
        except TclError:
            pass

        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self._validate_family = self.register(self.validate_font_family)
        self._validate_size = self.register(self.validate_font_size)

        # --- variable storing the chosen font
        self.res = ''

        style = Style(self)
        style.configure('prev.TLabel')
        bg = style.lookup('TLabel', 'background')
        self.configure(bg=bg)

        # --- family list
        self.fonts = list(set(families()))
        self.fonts.append('TkDefaultFont')
        self.fonts.sort()
        for i in range(len(self.fonts)):
            self.fonts[i] = self.fonts[i].replace(' ', '\\ ')
        max_length = int(2.5 * max([len(font) for font in self.fonts])) // 3 - 2
        self.sizes = ['%i' % i for i in (list(range(6, 17)) + list(range(18, 32, 2)) + list(range(36, 48, 4)))]
        # --- font default
        font_dict['weight'] = font_dict.get('weight', 'normal')
        font_dict['slant'] = font_dict.get('slant', 'roman')
        font_dict['underline'] = font_dict.get('underline', False)
        font_dict['overstrike'] = font_dict.get('overstrike', False)
        font_dict['family'] = font_dict.get('family', self.fonts[0].replace('\\ ', ' '))
        font_dict['size'] = font_dict.get('size', 10)

        # --- format list
        self.formats = ['Regular', 'Italic', 'Bold', 'Bold Italic']

        # --- creation of the widgets
        self.font_family = StringVar(self, ' '.join(self.fonts))
        self.font_size = StringVar(self, ' '.join(self.sizes))
        self.format_type = StringVar(self, self.formats)
        self.var_bold = BooleanVar(self, font_dict['weight'] == 'bold')
        self.var_italic = BooleanVar(self, font_dict['slant'] == 'italic')

        # ------ Size and family
        self.var_size = StringVar(self)
        self.entry_family = Entry(self, width=max_length, validate='key',
                                  validatecommand=(self._validate_family, '%d', '%S',
                                                   '%i', '%s', '%V'))
        self.entry_size = Entry(self, width=8, validate='key',
                                textvariable=self.var_size,
                                validatecommand=(self._validate_size, '%d', '%P', '%V'))

        self.entry_format = Entry(self)

        self.list_family = Listbox(self, selectmode='browse',
                                   listvariable=self.font_family,
                                   highlightthickness=0,
                                   exportselection=False,
                                   width=max_length,
                                   height=6)
        self.list_size = Listbox(self, selectmode='browse',
                                 listvariable=self.font_size,
                                 highlightthickness=0,
                                 exportselection=False,
                                 width=6,
                                 height=6)
        self.list_format = Listbox(self, selectmode='browse',
                                   listvariable=self.format_type,
                                   highlightthickness=0,
                                   exportselection=False,
                                   width=12,
                                   height=6)
        self.scroll_family = Scrollbar(self, orient='vertical',
                                       command=self.list_family.yview)
        self.scroll_size = Scrollbar(self, orient='vertical',
                                     command=self.list_size.yview)
        self.scroll_format = Scrollbar(self, orient='vertical',
                                       command=self.list_format.yview)
        self.family_label = Label(self, text='Font:')
        self.style_label = Label(self, text='Font style:')
        self.size_label = Label(self, text='Size:')

        self.script_label = Label(self, text='Script:')
        self.script_box = Combobox(self, values=['Western'])

        self.more_fonts_label = Lbl(self, text='Show more fonts', underline=1, fg='blue', cursor='hand2')
        f = Font(self.more_fonts_label, self.more_fonts_label.cget("font"))
        f.configure(underline=True)
        self.more_fonts_label.configure(font=f)

        self.preview_font = Font(self, **font_dict)
        if len(text) > 30:
            text = text[:30]
        self.preview_window = LabelFrame(self, relief='groove', text='Sample', bd=1)

        # --- widget configuration
        self.list_family.configure(yscrollcommand=self.scroll_family.set)
        self.list_size.configure(yscrollcommand=self.scroll_size.set)
        self.list_format.configure(yscrollcommand=self.scroll_format.set)

        self.entry_family.insert(0, font_dict['family'])
        self.entry_family.selection_clear()
        self.entry_family.icursor('end')
        self.entry_format.insert(0, self.formats[1])
        self.entry_format.selection_clear()
        self.entry_format.icursor('end')
        self.entry_size.insert(0, font_dict['size'])

        try:
            i = self.fonts.index(self.entry_family.get().replace(' ', '\\ '))
        except ValueError:
            # unknown font
            i = 0
        self.list_family.selection_clear(0, 'end')
        self.list_family.selection_set(i)
        self.list_family.see(i)
        try:
            i = self.sizes.index(self.entry_size.get())
            self.list_size.selection_clear(0, 'end')
            self.list_size.selection_set(i)
            self.list_size.see(i)
        except ValueError:
            # size not in listtsg
            pass

        # font family location config
        self.family_label.grid(row=0, column=0, sticky='nsew', pady=(10, 1), padx=(10, 1))
        self.entry_family.grid(row=1, column=0, sticky='nsew', pady=(1, 1), padx=(10, 0), columnspan=2)
        self.list_family.grid(row=2, column=0, sticky='nsew', pady=(1, 10), padx=(10, 0))
        self.scroll_family.grid(row=2, column=1, sticky='ns', pady=(1, 10))

        # font style/format location config
        self.style_label.grid(row=0, column=2, sticky='nsew', pady=(10, 1), padx=(15, 1))
        self.entry_format.grid(row=1, column=2, sticky='nsew', pady=(1, 1), padx=(15, 0), columnspan=2)
        self.list_format.grid(row=2, column=2, sticky='nsew', pady=(1, 10), padx=(15, 0))
        self.scroll_format.grid(row=2, column=3, sticky='ns', pady=(1, 10))

        # font size location config
        self.size_label.grid(row=0, column=4, sticky='nsew', pady=(10, 1), padx=(15, 1))
        self.entry_size.grid(row=1, column=4, sticky='nsew', pady=(1, 1), padx=(15, 10), columnspan=2)
        self.list_size.grid(row=2, column=4, sticky='nsew', pady=(1, 10), padx=(15, 0))
        self.scroll_size.grid(row=2, column=5, sticky='nsew', pady=(1, 10), padx=(0, 10))

        # font preview location config
        self.preview_window.grid(row=4, column=2, columnspan=4, sticky='nsew', rowspan=2, padx=15, pady=(0, 10),
                                 ipadx=10, ipady=10)
        self.preview_window.config(height=75)
        preview = Label(self.preview_window, text=text, font=self.preview_font, anchor='center')
        preview.place(relx=0.5, rely=0.5, anchor='center')

        self.script_label.grid(row=6, column=2, sticky='nsw', padx=(15, 0))
        self.script_box.grid(row=7, column=2, sticky='nsw', pady=(1, 30), padx=(15, 0))
        self.script_box.current(0)

        self.more_fonts_label.grid(row=8, column=0, pady=(35, 20), padx=(15, 0), sticky='nsw')

        button_frame = Frame(self)
        button_frame.grid(row=9, column=2, columnspan=4, pady=(0, 10), padx=(10, 0))

        Button(button_frame, text='Ok', command=self.ok).grid(row=0, column=0, padx=4, sticky='ew')
        Button(button_frame, text='Cancel', command=self.quit).grid(row=0, column=1, padx=4, sticky='ew')

        self.list_family.bind('<<ListboxSelect>>', self.update_entry_family)
        self.list_format.bind('<<ListboxSelect>>', self.update_entry_format)
        self.list_size.bind('<<ListboxSelect>>', self.update_entry_size, add=True)
        self.list_family.bind('<KeyPress>', self.keypress)
        self.entry_family.bind('<Return>', self.change_font_family)
        self.entry_family.bind('<Tab>', self.tab)
        self.entry_size.bind('<Return>', self.change_font_size)
        self.more_fonts_label.bind('<Button-1>', search_fonts)

        self.entry_family.bind('<Down>', self.down_family)
        self.entry_size.bind('<Down>', self.down_size)
        self.entry_family.bind('<Up>', self.up_family)
        self.entry_size.bind('<Up>', self.up_size)
        self.bind_class('TEntry', '<Control-a>', self.select_all)

        self.wait_visibility(self)
        self.grab_set()
        self.entry_family.focus_set()
        self.lift()

    def update_entry_format(self, _):
        style = self.list_format.get(self.list_format.curselection()[0])
        self.entry_format.delete(0, 'end')
        self.entry_format.insert(0, style)
        self.entry_format.selection_clear()
        self.entry_format.icursor('end')

        if style == self.formats[0]:
            self.var_italic = FALSE
            self.var_bold = FALSE
        elif style == self.formats[1]:
            self.var_italic = TRUE
            self.var_bold = FALSE
        elif style == self.formats[2]:
            self.var_italic = FALSE
            self.var_bold = TRUE
        elif style == self.formats[3]:
            self.var_italic = TRUE
            self.var_bold = TRUE
        else:
            log.error('invalid style')

        self.preview_font.configure(weight=['normal', 'bold'][self.var_bold],
                                    slant=['roman', 'italic'][self.var_italic])


def search_fonts(*_):
    url = 'https://www.bing.com/search?q=' + 'how+to+get+more+fonts+in+windows+10'
    webbrowser.open(url, 2)


def ask_font(master=None, text='aBbYyZz', title='Font', **font_args):
    chooser = FontChooser(master, font_args, text, title)
    chooser.wait_window(chooser)
    return chooser.get_res()
