import os
import tkinter as tk
import webbrowser
import logging as log
import tkfontchooser
from datetime import datetime
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import font
import findwidget


class Interface(tk.Frame):
    def __init__(self, master=None, *kwargs):
        tk.Frame.__init__(self, master)
        self.root = master
        self.__init_window()

    def __init_window(self):
        self.text_area = tk.Text(self.root, undo=True)

        self.__show_status_bar = tk.BooleanVar()
        self.__show_status_bar.set(False)

        self.word_wrap = tk.BooleanVar()
        self.word_wrap.set(True)
        self.counter = 0

        self.fnt = tk.font.Font(family="Courier New", size=10)
        self.text_area.config(font=self.fnt, wrap=tk.WORD)

        # To add scrollbar
        self.scroll_bar_x = tk.Scrollbar(self.text_area, orient=tk.HORIZONTAL)
        self.scroll_bar_y = tk.Scrollbar(self.text_area)
        __file = None

        try:
            pass
            self.root.wm_iconbitmap('notepad.ico')
        except tk.TclError:
            pass

        # Set the window text
        self.root.title('Untitled - Notepad')

        # To make the text area auto resizable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.text_area.grid(sticky=tk.N + tk.E + tk.W + tk.S)

        self.scroll_bar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_bar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Scrollbar will adjust automatically according to the content
        self.scroll_bar_x.config(command=self.text_area.xview)
        self.text_area.config(xscrollcommand=self.scroll_bar_x.set, yscrollcommand=self.scroll_bar_y.set)

        self.build_status_bar()
        self.__build_context_menu()
        self.__build_menu_bar()
        self.bind_shortcuts()

    def __build_menu_bar(self):
        # main and submenus
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.__format_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.thisViewMenu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)

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
        # self.edit_menu.add_command(label='Search with Bing... ', underline=0, accelerator='Ctrl+B',
        #                           command=self.search_selected_text)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Find...', underline=0, accelerator='Ctrl+F', command=self.show_find)
        self.edit_menu.add_command(label='Find Next', underline=5, accelerator='F3', command=self.show_find)
        self.edit_menu.add_command(label='Replace...', underline=0, accelerator='Ctrl+H', command=self.paste)
        self.edit_menu.add_command(label='Go To...', underline=0, accelerator='Ctrl+G', command=self.paste)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Select All', underline=7, accelerator='Ctrl+A', command=self.select_all)
        self.edit_menu.add_command(label='Time/Date', underline=5, accelerator='F5', command=self.time_date)

        # Format Menu
        self.menu_bar.add_cascade(label='Format', underline=0, menu=self.__format_menu)
        self.__format_menu.add_checkbutton(label='Word Wrap', underline=0, variable=self.word_wrap,
                                           command=self.toggle_word_wrap)
        self.__format_menu.add_command(label='Font...', underline=0, command=self.set_font)

        # View Menu
        self.menu_bar.add_cascade(label='View', underline=1, menu=self.thisViewMenu)
        self.thisViewMenu.add_checkbutton(label='Status Bar', underline=0,
                                          variable=self.__show_status_bar,
                                          command=self.toggle_status_bar)

        # Help Menu
        self.menu_bar.add_cascade(label='Help', underline=0, menu=self.help_menu)
        self.help_menu.add_command(label='View Help', underline=5, command=self.get_help)
        self.help_menu.add_separator()
        self.help_menu.add_command(label='About Notepad', underline=0, command=show_about)

        self.root.config(menu=self.menu_bar)

    def __build_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label='Undo', underline=2, accelerator='Ctrl+Z', command=self.undo)
        self.context_menu.add_separator()
        self.context_menu.add_command(label='Cut', underline=2, accelerator='Ctrl+X', command=self.cut)
        self.context_menu.add_command(label='Copy', underline=0, accelerator='Ctrl+C', command=self.copy)
        self.context_menu.add_command(label='Paste', underline=0, accelerator='Ctrl+V', command=self.paste)
        self.context_menu.add_command(label='Delete', underline=2, accelerator='Del', command=self.delete)
        self.context_menu.add_separator()
        self.context_menu.add_command(label='Select All', underline=2, accelerator='Ctrl+A', command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label='Search with Bing... ', underline=0, accelerator='Ctrl+B',
                                      command=self.search_selected_text)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.context_menu.grab_release()

    def set_font(self):
        fnt = tkfontchooser.askfont(family=self.fnt.actual(option='family'),
                                    size=self.fnt.actual(option='size'),
                                    weight=self.fnt.actual(option='weight'),
                                    slant=self.fnt.actual(option='slant'),
                                    underline=self.fnt.actual(option='underline'),
                                    overstrike= self.fnt.actual(option='overstrike'))

        if fnt:
            self.fnt = tk.font.Font(family=fnt['family'],
                                    size=int(fnt['size']),
                                    weight=fnt['weight'],
                                    slant=fnt['slant'],
                                    underline=int(fnt['underline']),
                                    overstrike=int(fnt['overstrike']))

            self.text_area.config(font=self.fnt)

    def build_status_bar(self):
        self.status_bar = tk.Label(self.root, text=str(self.counter) + "Ln 1, Col 1\t", bd=1, relief=tk.SUNKEN, anchor=tk.E)

    def toggle_status_bar(self):
        if self.__show_status_bar.get():
            self.status_bar.grid(sticky=tk.S + tk.E + tk.W)
        else:
            self.status_bar.grid_forget()

    def toggle_word_wrap(self):
        if self.word_wrap.get():
            self.text_area.config(wrap=tk.WORD)
            log.debug("rap on")
        else:
            self.text_area.config(wrap=tk.NONE)
            log.debug("rap off")

    def bind_shortcuts(self):
        self.root.bind_class('Text', '<Control-a>', self.select_all)
        self.root.bind_class('Text', '<Control-A>', self.select_all)
        self.root.bind_class('Text', '<Control-s>', save_file)
        self.root.bind_class('Text', '<Control-S>', save_file)
        self.root.bind_class('Text', '<Control-n>', new_file)
        self.root.bind_class('Text', '<Control-N>', new_file)
        self.root.bind_class('Text', '<Control-b>', self.search_selected_text)
        self.root.bind_class('Text', '<Control-B>', self.search_selected_text)
        self.root.bind_class('Text', '<Control-f>', self.show_find)
        self.root.bind_class('Text', '<Control-F>', self.show_find)
        self.root.bind_class('Text', '<Control-h>', self.show_find_replace)
        self.root.bind_class('Text', '<Control-H>', self.show_find_replace)
        self.root.bind_class('Text', '<F5>', self.time_date)
        self.text_area.bind_class(self.text_area, '<Any-KeyPress>', self.on_key)
        self.text_area.bind_class(self.text_area, '<Button-1>', self.on_click)
        self.text_area.bind_class(self.text_area, '<Button-3>', self.show_context_menu)

    def quit_application(self):
        self.root.destroy()
        exit()

    def undo(self, *args):
        self.text_area.event_generate('<<Undo>>')

    def on_key(self, event=None):
        self.update_status_bar(tk.INSERT)

    def on_click(self, event=None):
        self.update_status_bar(tk.CURRENT)

    def update_status_bar(self, obj):
        row, col = self.text_area.index(obj).split('.')
        self.status_bar.config(text=str('Ln ' + row + ', Col ' + col + ' \t'))

    def get_index(text, index):
        return tuple(map(int, str.split(text.index(index), ".")))

    def cut(self, *args):
        self.text_area.event_generate('<<Cut>>')

    def copy(self, *args):
        self.text_area.event_generate('<<Copy>>')

    def paste(self, *args):
        self.text_area.event_generate('<<Paste>>')

    def select_all(self, *args):
        self.text_area.tag_add('sel', '1.0', 'end')

    def delete(self):
        self.text_area.event_generate('<Delete>')

    def search_selected_text(self, *args):
        try:
            s = self.text_area.selection_get()
            if s is not None:
                search_with_bing(s)
            else:
                log.debug('selection was empty, not searching with bing')
        except tk.TclError:
            print('TclError - Probably because nothing was selected ')

    def time_date(self, *kwargs):
        now = datetime.now()
        # s = now.strftime("%X %x")
        # s = now.ctime()
        s = now.strftime("%I:%M %p %m/%d/%Y\n")
        self.text_area.insert(tk.INSERT, s)

    def show_find(self, *args):
        findwidget.FindWindow(master=self)

    def show_find_replace(self, *args):
        findwidget.FindReplaceWindow(master=self)

    @staticmethod
    def get_help():
        search_with_bing("get+help+with+notepad+in+windows+10")

    def run(self):
        # Run main application
        self.root.mainloop()

    def set_title(self, string):
        self.root.title(string + ' - Notepad')

    def clear_text(self):
        self.text_area.delete(1.0, tk.END)

    def get_text(self):
        return self.text_area.get(1.0, tk.END)

    def write_text(self, text, start_index=1.0):
        self.text_area.insert(start_index, text)


def open_file():
    global file
    file = askopenfilename(defaultextension='.txt',
                           filetypes=[('All Files', '*.*'),
                                      ('Text Documents', '*.txt')])

    log.info("attempting to open file " + str(file))

    try:
        f = open(file, 'r')
        notepad.clear_text()
        notepad.write_text(f.read())
        notepad.set_title(os.path.basename(file))
    except FileNotFoundError:
        log.error('FileNotFoundError', file)


def new_file():
    global file
    notepad.set_title('Untitled')
    file = ''
    notepad.clear_text()


def save_file_as():
    global file

    try:
        file = asksaveasfilename(initialfile='*.txt', defaultextension='.txt',
                                 filetypes=[('All Files', '*.*'), ('Text Documents', '*.txt')])

        if file != '':
            # Try to save the file
            notepad.set_title(os.path.basename(file))
            f = open(file, 'w')
            f.write(notepad.get_text())
            # Change the window title
            f.close()

    except tk.TclError:
        messagebox.showerror('Notepad', 'Error saving file.')


def save_file():
    global file

    if file != '':
        try:
            print(file)
            f = open(file, 'w')
            f.write(notepad.get_text())
            f.close()

        except tk.TclError:
            save_file_as()
    else:
        save_file_as()


def search_with_bing(string):
    url = "https://www.bing.com/search?q=" + string
    webbrowser.open(url, 2)


def show_about():
    messagebox.showinfo('Notepad', 'Microsoft Windows\n(c) 1983 Microsoft Corporation')


# Run main application

# global vars
file = ''     # path to current file
log.basicConfig(level=log.INFO)

window = tk.Tk()
window.geometry("800x600")
notepad = Interface(window)
notepad.run()
