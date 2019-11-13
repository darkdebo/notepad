import logging as log
import os
import hashlib
import webbrowser
from datetime import datetime
from tkinter import Frame, Text, LabelFrame, Scrollbar, Menu, Button, Checkbutton, Radiobutton, Label, Entry, font, \
    BooleanVar, TclError, Tk, HORIZONTAL, VERTICAL, WORD, SUNKEN, INSERT, CURRENT, NONE, END, Toplevel, messagebox, \
    SEL_FIRST, SEL_LAST
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import fontpicker


class Interface(Frame):
    def __init__(self, master=None, *_):
        Frame.__init__(self, master)
        self.master = master

        # settings variables
        self.word_wrap = BooleanVar()
        self.word_wrap.set(True)
        self.__show_status_bar = BooleanVar()
        self.__show_status_bar.set(True)
        self.fnt = font.Font(family="Courier New", size=10)
        self.find_open = False
        self.replace_open = False
        self.goto_open = False
        self.prior_search = ''
        self.prior_goto = ''

        # init methods
        self.__init_main_window()
        self.__build_status_bar()
        self.__build_menu_bar()
        self.__bind_shortcuts()
        self.toggle_word_wrap()
        self.context_menu = Menu(self.master, tearoff=0)

        self.last_hash = get_signature(self.text_area.get(1.0, END))

    def __init_main_window(self):
        self.text_area = Text(self.master, undo=True)
        self.text_area.config(font=self.fnt, wrap=WORD)

        # To add scrollbar
        self.scroll_bar_x = Scrollbar(self.master, orient=HORIZONTAL)
        self.scroll_bar_y = Scrollbar(self.master, orient=VERTICAL)
        __file = None

        try:
            self.master.wm_iconbitmap('notepad.ico')
        except TclError:
            log.error("unable to set icon to notepad.ico")
            pass

        # Set the window text
        self.master.title('Untitled - Notepad')

        # To make the text area auto resizable
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.text_area.grid(column=0, row=0, sticky='nsew')

        self.scroll_bar_y.grid(column=1, row=0, sticky='nsew')
        self.scroll_bar_x.grid(column=0, row=1, stic='nsew')

        # Scrollbar will adjust automatically according to the content
        self.scroll_bar_x.config(command=self.text_area.xview)
        self.scroll_bar_y.config(command=self.text_area.yview)
        self.text_area.config(xscrollcommand=self.scroll_bar_x.set, yscrollcommand=self.scroll_bar_y.set)

        self.text_area.focus()

    def __build_menu_bar(self):
        # main and submenus
        self.menu_bar = Menu(self.master)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.format_menu = Menu(self.menu_bar, tearoff=0)
        self.thisViewMenu = Menu(self.menu_bar, tearoff=0)
        self.help_menu = Menu(self.menu_bar, tearoff=0)

        # File Menu
        self.menu_bar.add_cascade(label='File', underline=0, menu=self.file_menu)
        self.file_menu.add_command(label='New', underline=0, accelerator='Ctrl+N', command=new_file)
        self.file_menu.add_command(label='Open...', underline=0, accelerator='Ctrl+O', command=open_file)
        self.file_menu.add_command(label='Save', underline=0, accelerator='Ctrl+S', command=save_file)
        self.file_menu.add_command(label='Save As...', underline=5, command=save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Page Setup...', underline=5, accelerator='Ctrl+S', command=save_file)
        self.file_menu.add_command(label='Print', underline=0, accelerator='Ctrl+P', command=save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', underline=1, command=self.quit_application)

        # Edit Menu
        self.menu_bar.add_cascade(label='Edit', underline=0, menu=self.edit_menu)
        self.edit_menu.add_command(label='Undo', underline=0, accelerator='Ctrl+Z', command=self.undo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Cut', underline=2, accelerator='Ctrl+X', command=self.cut)
        self.edit_menu.add_command(label='Copy', underline=0, accelerator='Ctrl+C', command=self.copy)
        self.edit_menu.add_command(label='Paste', underline=0, accelerator='Ctrl+V', command=self.paste)
        self.edit_menu.add_command(label='Delete', underline=2, accelerator='Del', command=self.delete)
        self.edit_menu.add_command(label='Search with Bing... ', underline=0, accelerator='Ctrl+B',
                                   command=self.search_selected_text)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Find...', underline=0, accelerator='Ctrl+F', command=self.show_find)
        self.edit_menu.add_command(label='Find Next', underline=5, accelerator='F3', command=self.find_next)
        self.edit_menu.add_command(label='Replace...', underline=0, accelerator='Ctrl+H',
                                   command=self.show_find_replace)
        self.edit_menu.add_command(label='Go To...', underline=0, accelerator='Ctrl+G', command=self.show_goto)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Select All', underline=7, accelerator='Ctrl+A',
                                   command=lambda: self.select_all())
        self.edit_menu.add_command(label='Time/Date', underline=5, accelerator='F5', command=self.time_date)

        # Format Menu
        self.menu_bar.add_cascade(label='Format', underline=0, menu=self.format_menu)
        self.format_menu.add_checkbutton(label='Word Wrap', underline=0, variable=self.word_wrap,
                                         command=self.toggle_word_wrap)
        self.format_menu.add_command(label='Font...', underline=0, command=self.set_font)

        # View Menu
        self.menu_bar.add_cascade(label='View', underline=1, menu=self.thisViewMenu)
        self.thisViewMenu.add_checkbutton(label='Status Bar', underline=0, variable=self.__show_status_bar,
                                          command=self.toggle_status_bar)

        # Help Menu
        self.menu_bar.add_cascade(label='Help', underline=0, menu=self.help_menu)
        self.help_menu.add_command(label='View Help', underline=5, command=self.get_help)
        self.help_menu.add_separator()
        self.help_menu.add_command(label='About Notepad', underline=0, command=show_about)

        self.master.config(menu=self.menu_bar)

    def show_context_menu(self, event):
        try:
            self.context_menu = Menu(self.master, tearoff=0)
            self.context_menu.add_command(label='Undo', underline=2, accelerator='Ctrl+Z', command=self.undo)
            self.context_menu.add_separator()
            self.context_menu.add_command(label='Cut', underline=2, accelerator='Ctrl+X', command=self.cut)
            self.context_menu.add_command(label='Copy', underline=0, accelerator='Ctrl+C', command=self.copy)
            self.context_menu.add_command(label='Paste', underline=0, accelerator='Ctrl+V', command=self.paste)
            self.context_menu.add_command(label='Delete', underline=2, accelerator='Del', command=self.delete)
            self.context_menu.add_separator()
            self.context_menu.add_command(label='Select All', underline=2, accelerator='Ctrl+A',
                                          command=self.select_all)
            self.context_menu.add_separator()
            self.context_menu.add_command(label='Search with Bing... ', underline=0, accelerator='Ctrl+B',
                                          command=self.search_selected_text)
            self.context_menu.tk_popup(event.x_root, event.y_root)

        finally:
            self.context_menu.grab_release()

    def set_font(self):
        fnt = fontpicker.ask_font(family=self.fnt.actual(option='family'),
                                  size=self.fnt.actual(option='size'),
                                  weight=self.fnt.actual(option='weight'),
                                  slant=self.fnt.actual(option='slant'))

        if fnt:
            self.fnt = font.Font(family=fnt['family'],
                                 size=int(fnt['size']),
                                 weight=fnt['weight'],
                                 slant=fnt['slant'])

            self.text_area.config(font=self.fnt)

    def __build_status_bar(self):
        self.status_bar = Label(self.master, text="Ln 1, Col 1\t", bd=1, relief=SUNKEN, anchor='e')
        self.toggle_status_bar()

    def toggle_status_bar(self):
        if self.__show_status_bar.get():
            self.status_bar.grid(sticky='sew')
        else:
            self.status_bar.grid_forget()

    def toggle_word_wrap(self):
        if self.word_wrap.get():
            self.text_area.config(wrap=WORD)
            self.scroll_bar_x.grid_forget()
            log.info("word wrap on, scroll bar off")
        else:
            self.text_area.config(wrap=NONE)
            self.scroll_bar_x.grid(column=0, row=1, sticky='nsew')
            log.info("word wrap off, scroll bar on")

    def __bind_shortcuts(self):
        self.master.bind_class('Text', '<Control-a>', self.select_all)
        self.master.bind_class('Text', '<Control-A>', self.select_all)
        self.master.bind_class('Text', '<Control-s>', save_file)
        self.master.bind_class('Text', '<Control-S>', save_file)
        self.master.bind_class('Text', '<Control-n>', new_file)
        self.master.bind_class('Text', '<Control-N>', new_file)
        self.master.bind_class('Text', '<Control-b>', self.search_selected_text)
        self.master.bind_class('Text', '<Control-B>', self.search_selected_text)
        self.master.bind_class('Text', '<Control-f>', self.show_find)
        self.master.bind_class('Text', '<Control-F>', self.show_find)
        self.master.bind_class('Text', '<Control-h>', self.show_find_replace)
        self.master.bind_class('Text', '<Control-H>', self.show_find_replace)
        self.master.bind_class('Text', '<Control-g>', self.show_goto)
        self.master.bind_class('Text', '<Control-G>', self.show_goto)
        self.master.bind_class('Text', '<F5>', self.time_date)
        self.master.bind_class('Text', '<F3>', self.find_next)
        self.text_area.bind_class(self.text_area, '<Any-KeyPress>', self.on_key)
        self.text_area.bind_class(self.text_area, '<Button-1>', self.on_click)
        self.text_area.bind_class(self.text_area, '<Button-3>', self.show_context_menu)

    def quit_application(self):
        if notepad.has_changed():
            save_box = messagebox.askquestion('Confirm save', 'Do you want to save before closing this file?',
                                              icon='warning')
            if save_box == 'yes':
                save_file()
        self.master.destroy()
        exit()

    def undo(self, *_):
        self.text_area.event_generate('<<Undo>>')

    def on_key(self, *_):
        self.update_status_bar(INSERT)

    def on_click(self, *_):
        self.update_status_bar(CURRENT)

        try:
            self.context_menu.destroy()
        except AttributeError:
            log.warning('error occurred while trying to exit context menu, probably not instansiated')

    def update_status_bar(self, obj):
        row, col = self.text_area.index(obj).split('.')
        self.status_bar.config(text=str('Ln ' + row + ', Col ' + col + ' \t'))

    def cut(self, *_):
        self.text_area.event_generate('<<Cut>>')

    def copy(self, *_):
        self.text_area.event_generate('<<Copy>>')

    def paste(self, *_):
        self.text_area.event_generate('<<Paste>>')

    def select_all(self, *_):
        self.text_area.tag_add('sel', '1.0', 'end')

    def delete(self, *_):
        self.text_area.event_generate('<Delete>')

    def search_selected_text(self, *_):
        try:
            s = self.text_area.selection_get()
            if s is not None:
                search_with_bing(s)
            else:
                log.debug('selection was empty, not searching with bing')
        except TclError:
            print('TclError - Probably because nothing was selected ')

    def time_date(self, *_):
        now = datetime.now()
        s = now.strftime("%I:%M %p %m/%d/%Y")
        self.text_area.insert(INSERT, s)

    def show_find(self, *_):
        if not self.find_open:
            self.find_open = True
            FindWindow(master=self)

    def show_find_replace(self, *_):
        if not self.replace_open:
            self.replace_open = True
            FindReplaceWindow(master=self)

    def show_goto(self, *_):
        if not self.goto_open:
            self.goto_open = True
            GotoWindow(master=self)

    @staticmethod
    def get_help():
        search_with_bing("get+help+with+notepad+in+windows+10")

    def run(self):
        # Run main application
        self.master.mainloop()

    def set_title(self, string):
        self.master.title(string + ' - Notepad')

    def clear_text(self):
        self.text_area.delete(1.0, END)

    def get_text(self):
        return self.text_area.get(1.0, END)

    def write_text(self, text, start_index=1.0):
        self.text_area.insert(start_index, text)

    def find_next(self, _):
        search_string = self.prior_search

        location = self.text_area.search(search_string, self.text_area.index(INSERT),
                                         nocase=True)
        log.info('searching next -- forwards')

        if location != '':
            log.info('found ' + search_string + ' at position ' + location)

            row, col = get_index(location)
            end_col = str(col + len(search_string))
            end_location = str(str(row) + '.' + end_col)

            self.text_area.mark_set("insert", end_location)
            self.text_area.see("insert")
            self.text_area.tag_remove('sel', "1.0", END)
            self.text_area.tag_raise("sel")
            self.text_area.tag_add('sel', location, end_location)
            self.text_area.focus()
        else:
            log.warning(search_string + 'string not found')

    def has_changed(self):
        if get_signature(self.text_area.get(1.0, END)) == self.last_hash:
            log.info('file has changed')
            return False
        else:
            log.info('file has not changed')
            return True


def get_index(index):
    return tuple(map(int, str.split(index, ".")))


class GotoWindow(Toplevel):
    def __init__(self, master, **kwargs):
        Toplevel.__init__(self, master, **kwargs)

        self.master = master

        try:
            self.wm_iconbitmap('transparent.ico')
        except TclError:
            log.info("unable to set icon to transparent.ico, window manager may not support")
            pass

        self.title('Go To Line')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit)

        # search string box
        self.find_label = Label(self, text='Line Number:')
        self.find_label.grid(row=0, column=0, sticky='nw', pady=(10, 0), padx=5)
        self.entry_line = Entry(self, width=35)
        self.entry_line.grid(row=1, column=0, columnspan=2, sticky='new', padx=5, pady=(0, 10))
        self.entry_line.focus()

        # find next, cancel buttons
        self.button_box = Frame(self)
        Button(self.button_box, text="Go To",
               command=self.goto).grid(row='0', column=0, padx=0, pady=(0, 5), sticky='e')
        Button(self.button_box, text="Cancel",
               command=self.quit).grid(row='0', column=1, padx=(5, 10), pady=(0, 5), sticky='e')
        self.button_box.grid(column=1, row=2)

    def goto(self):
        line = self.entry_line.get()
        try:
            line = int(line)
            self.master.text_area.mark_set("insert", "%d.0" % line)
            self.master.text_area.see("insert")

        except ValueError:
            log.ERROR('Value not integer')

    def quit(self):
        self.master.goto_open = False
        self.destroy()


class FindReplaceWindow(Toplevel):
    def __init__(self, master, **kwargs):
        Toplevel.__init__(self, master, **kwargs)

        self.master = master
        self.attributes('-topmost', True)

        self.direction = BooleanVar()
        self.direction.set(False)
        self.no_case_match = BooleanVar()
        self.no_case_match.set(False)

        self.title('Replace')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit)

        try:
            self.wm_iconbitmap('transparent.ico')
        except TclError:
            log.warning("unable to set icon to transparent.ico")
            pass

        # search string box
        self.find_label = Label(self, text='Find what:')
        self.find_label.grid(row=1, column=1, sticky='new', pady=(12, 10), padx=(5, 10))
        self.entry_find = Entry(self, width=25)
        self.entry_find.insert(END, self.master.prior_search)
        self.entry_find.grid(row=1, column=2, columnspan=2, sticky='new', padx=(0, 0), pady=(10, 10))

        # replace string box
        self.replace_label = Label(self, text='Replace:')
        self.replace_label.grid(row=2, column=1, sticky='new', pady=(6, 10), padx=(5, 10))
        self.entry_replace = Entry(self, width=25)
        self.entry_replace.grid(row=2, column=2, columnspan=2, sticky='new', padx=(0, 0), pady=(5, 10))

        # buttons
        self.button_frame = Frame(self)
        self.button_frame.grid(row=1, column=4, rowspan=4, pady=(10, 0), padx=(10, 5), sticky='ne')
        Button(self.button_frame, text="Find next",
               command=self.find).grid(row=0, column=0, padx=5, pady=(0, 5), sticky='new')
        Button(self.button_frame, text="Cancel",
               command=self.quit).grid(row=1, column=0, padx=5, pady=(0, 5), sticky='new')
        Button(self.button_frame, text="Replace",
               command=self.replace).grid(row=2, column=0, padx=5, pady=(0, 5), sticky='new')
        Button(self.button_frame, text="Replace all",
               command=self.quit).grid(row=3, column=0, padx=5, pady=(0, 5), sticky='new')

        # match case checkbox
        self.match_case = Checkbutton(self, text='Match case')
        self.match_case.grid(row=3, column=1, sticky="sw", padx=5, pady=0, columnspan=2)
        self.match_whole_word = Checkbutton(self, text='Match whole word only')
        self.match_whole_word.grid(row=4, column=1, sticky="sw", padx=5, pady=10, columnspan=2)

        self.entry_find.focus()

    def find(self):
        search_string = self.entry_find.get()

        if self.no_case_match.get():
            match_case = False
        else:
            match_case = True

        if self.direction.get():
            row, col = get_index(self.master.text_area.index(INSERT))
            beg_col = str(col - len(search_string))
            beg_location = str(str(row) + '.' + beg_col)
            location = self.master.text_area.search(search_string, self.master.text_area.index(beg_location),
                                                    backwards=True,
                                                    nocase=match_case)
            log.info('searching backwards')
        else:
            log.info('searching forwards')
            location = self.master.text_area.search(search_string, self.master.text_area.index(INSERT),
                                                    nocase=match_case)

        if location != '':
            log.info('found ' + search_string + ' at position ' + location)
            self.master.prior_search = search_string

            row, col = get_index(location)
            end_col = str(col + len(search_string))
            end_location = str(str(row) + '.' + end_col)

            self.master.text_area.mark_set("insert", end_location)
            self.master.text_area.see("insert")
            self.master.text_area.tag_remove('sel', "1.0", END)
            self.master.text_area.tag_raise("sel")
            self.master.text_area.tag_add('sel', location, end_location)
            self.master.text_area.focus()
        else:
            log.warning(search_string + 'string not found')

    def replace(self):
        replace_string = self.entry_replace.get()

        if self.master.prior_search != replace_string:
            self.master.prior_search = self.entry_find.get()

        search_string = self.master.prior_search

        try:
            if self.master.text_area.selection_get() == search_string:
                self.master.text_area.delete(SEL_FIRST, SEL_LAST)

                row, col = get_index(self.master.text_area.index(INSERT))
                self.master.text_area.insert(INSERT, replace_string)
                end_location = str(str(row) + '.' + str(col))

                self.master.text_area.tag_add('sel', end_location, INSERT)
                self.master.text_area.focus()

        except TclError:
            log.warning('TclError -> Invalid selection?')

        self.master.find_next()

    def quit(self):
        self.master.replace_open = False
        self.destroy()


class FindWindow(FindReplaceWindow):
    def __init__(self, master, **kwargs):
        Toplevel.__init__(self, master, **kwargs)

        self.master = master

        self.attributes('-topmost', True)

        self.direction = BooleanVar()
        self.direction.set(False)
        self.no_case_match = BooleanVar()
        self.no_case_match.set(False)

        self.title('Find')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit)

        try:
            self.wm_iconbitmap('transparent.ico')
        except TclError:
            log.error("unable to set icon to transparent.ico")
            pass

        # search string box
        self.find_label = Label(self, text='Find what:')
        self.find_label.grid(row=1, column=1, sticky='new', pady=(12, 10), padx=(5, 10))
        self.entry_find = Entry(self, width=25)
        self.entry_find.insert(END, self.master.prior_search)
        self.entry_find.grid(row=1, column=2, columnspan=2, sticky='new', padx=(0, 0), pady=(10, 10))

        # find next, cancel buttons
        self.button_frame = Frame(self)
        self.button_frame.grid(row=1, column=4, rowspan=2, pady=(10, 0), padx=(10, 5), sticky='ne')
        self.find_button = Button(self.button_frame, text="Find next",
                                  command=self.find).grid(row=0, column=0, padx=5, pady=(0, 0), sticky='ew')
        self.cancel_button = Button(self.button_frame, text="Cancel",
                                    command=self.quit).grid(row=1, column=0, padx=5, pady=(5, 0), sticky='ew')

        # key bindings
        self.bind_class('Text', 'Button', '<Return>', self.find)
        self.bind_class('Text', 'Button', '<Escape>', self.quit)

        # match case checkbox
        self.match_case = Checkbutton(self, text='Match case', variable=self.no_case_match)
        self.match_case.grid(row=2, column=1, sticky="sw", padx=5, pady=10, columnspan=2)

        # directional radiobutton
        self.direction_box = LabelFrame(self, text='Direction')
        self.direction_box.grid(row=2, column=3, sticky='ne', pady=(0, 10))
        self.up_button = Radiobutton(self.direction_box, text='Up', variable=self.direction, value=True)
        self.up_button.grid(row=1, column=1, padx=5)
        self.down_button = Radiobutton(self.direction_box, text='Down', variable=self.direction, value=False)
        self.down_button.grid(row=1, column=2, padx=(0, 5))

        self.entry_find.focus()

    def quit(self, *_):
        self.master.find_open = False
        self.destroy()


def open_file():
    global FILE
    line = ''

    if notepad.has_changed():
        save_box = messagebox.askquestion('Confirm save', 'Do you want to save before closing this file?',
                                          icon='warning')
        if save_box == 'yes':
            save_file()

    FILE = askopenfilename(defaultextension='.txt',
                           initialdir='.',
                           filetypes=[('All Files', '*.*'),
                                      ('Text Documents', '*.txt'),
                                      ('Log Files', '*.log')])

    try:
        log.info("attempting to open file " + str(FILE))
        f = open(FILE, 'r')
        notepad.clear_text()
        lines = f.read()
        f.close()
        notepad.write_text(lines)
        line = lines[:4]
        notepad.set_title(os.path.basename(FILE))
        log.info(str(FILE) + " opened")

    except TypeError:
        log.error('TypeError', FILE)
    except FileNotFoundError:
        log.error('FileNotFoundError', FILE)

    if line.upper() == '.LOG':
        log.info(FILE + ' is a log, appending time stamp.')
        notepad.time_date()


def new_file():
    global FILE
    if notepad.has_changed():
        save_box = messagebox.askquestion('Confirm save', 'Do you want to save before closing this file?',
                                          icon='warning')
        if save_box == 'yes':
            save_file()

    notepad.set_title('Untitled')
    FILE = ''
    notepad.clear_text()


def save_file_as():
    global FILE

    try:
        FILE = asksaveasfilename(initialfile='*.txt', defaultextension='.txt',
                                 filetypes=[('All Files', '*.*'), ('Text Documents', '*.txt')])

        if FILE != '':
            # Try to save the file
            notepad.set_title(os.path.basename(FILE))
            f = open(FILE, 'w')
            f.write(notepad.get_text())
            # Change the window title
            f.close()

    except TclError:
        messagebox.showerror('Notepad', 'Error saving file.')


def save_file(*_):
    global FILE

    if FILE != '':
        try:
            print(FILE)
            f = open(FILE, 'w')
            f.write(notepad.get_text())
            f.close()

        except TclError:
            save_file_as()
    else:
        save_file_as()


def search_with_bing(string):
    url = "https://www.bing.com/search?q=" + string
    webbrowser.open(url, 2)


def show_about():
    messagebox.showinfo('Notepad', 'Microsoft Windows\n(c) 1983 Microsoft Corporation')


def get_signature(contents):
    m = hashlib.md5()
    m.update(contents.encode('utf-8'))
    return m.hexdigest()


# global vars
FILE = ''  # path to current file
log.basicConfig(level=log.INFO)

window = Tk()
window.geometry("800x600")
notepad = Interface(window)
notepad.run()
