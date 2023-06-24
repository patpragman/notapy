import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import re
import webbrowser

from tkinter import filedialog as fd

import toml

import config
from menu_framework import FileMenu, AboutMenu, EditMenu

class Tag:

    def __init__(self,
                 name,
                 row_1,
                 start,
                 row_2,
                 end,
                 prefs=None,
                 url=None,
                 clickable=0):
        self.name = name
        self.start = f"{row_1}.{start}"
        self.end = f"{row_2}.{end}"

        self.clickable = clickable
        self.prefs = prefs


class App:
    def __init__(self):
        # set up the main window for the app
        self.root = tk.Tk()
        self.root.title('NotaPy')
        self.root.geometry('512x512')
        self.root.minsize(128, 256)
        self.root.maxsize(1024, 768)

        # tk variables
        self.search_bar_variable = tk.StringVar(self.root)
        self.file_path_variable = tk.StringVar(self.root,
                                               value=config.state['last_file']['path'])

        # program variables
        self.tag_list = []

        # top menu bar
        self.menu = tk.Menu(self.root)
        self.menu.add_cascade(label="File",
                              menu=FileMenu(self.menu, self,
                                            new_command=self.new_file_from_picker,
                                            load_command=self.select_file_from_picker,
                                            quit_command=self.quit,

                                            )
                              )
        self.menu.add_cascade(label="Edit",
                              menu=EditMenu(self.menu,
                                            self,
                                            paste_command=lambda e=None: self.paste(),
                                            cut_command=lambda e=None: self.cut(),
                                            copy_command=lambda e=None: self.copy(),
                                            select_all_command=lambda e=None: self.select_all()))
        self.menu.add_cascade(label="Info",
                              menu=AboutMenu(self.menu, self))

        self.root.config(menu=self.menu)

        # widgets
        self.top_label = tk.Label(self.root, textvariable=self.file_path_variable)
        self.search_bar_label = tk.Label(self.root,
                                         text="Search:")

        self.search_bar = tk.Entry(self.root)
        self.search_bar_results_label = tk.Label(self.root,
                                                 textvariable=self.search_bar_label)
        self.text_box = ScrolledText(self.root)

        # bind the keyboard controls
        self.search_bar.bind("<KeyRelease>", self._refresh)
        self.text_box.bind("<KeyRelease>", self._refresh)
        self.root.bind("<Escape>", lambda event: self.quit())

        # pack the widgets
        self.top_label.pack(fill=tk.X)
        self.search_bar_label.pack(fill=tk.X)
        self.search_bar.pack(fill=tk.X)
        self.search_bar_results_label.pack(fill=tk.X)
        self.search_bar_results_label.pack(fill=tk.X)
        self.text_box.pack(fill=tk.BOTH, expand=True)

        self._load(None)
        self._refresh(None)

    def cut(self):
        command = f'echo "{self.text_box.selection_get()[0:-1]}" | xclip -sel c -f'
        os.system(command)
        self.text_box.delete(tk.SEL_FIRST, tk.SEL_LAST)

    def paste(self):
        string_to_paste = self.root.clipboard_get()
        self.text_box.insert(tk.INSERT, string_to_paste)

    def copy(self):
        command = f'echo "{self.text_box.selection_get()[0:-1]}" | xclip -sel c -f'
        os.system(command)

    def select_all(self):
        self.text_box.tag_add(tk.SEL, "1.0", tk.END)
        self.text_box.mark_set(tk.INSERT, "1.0")
        self.text_box.see(tk.INSERT)

    def new_file_from_picker(self):
        fn = fd.asksaveasfilename(title="Create a new file")
        if fn:
            self._save(None)  # save what you were working on
            self._clear()
            self.file_path_variable.set(fn)
            os.system(f"touch {fn}")
            self._load(None)

    def select_file_from_picker(self):
        fn = fd.askopenfilename()
        if fn:
            self.file_path_variable.set(fn)
            self._load(None)

    def quit(self):
        self._save(None)
        quit()

    def _load(self, event):
        # load the text
        try:
            with open(self.file_path_variable.get(), 'r') as notes_file:
                self._clear()
                self.text_box.insert(tk.END,
                                     notes_file.read()
                                     )
        except FileNotFoundError as file_error:
            prompt = """I cannot find the file you were last working on, that or this is your first time using this
program.  Select "Yes" to create a new file, "No" to open a different file, and "Cancel" to quit."""

            answer = messagebox.askyesnocancel("Oh no!  File not found!", prompt)
            if answer:
                self.new_file_from_picker()
            elif answer is False:
                self.select_file_from_picker()
            else:
                quit()

            self._save(None)

        self._refresh(None)

    def _refresh(self, event):
        self._tag_update(event)
        self._save(event)

    def _tag_update(self, event):
        # get current text from the text_box
        current_text = self.text_box.get("1.0", tk.END)
        search_query = self.search_bar.get()

        # now, delete all old tags
        while self.tag_list:
            tag = self.tag_list.pop()
            self.text_box.tag_delete(tag.name)

        format_dictionary = {k: v for k, v in config.prefs.items()}
        if search_query:
            format_dictionary[self.search_bar.get()] = format_dictionary.pop("match")
        else:
            format_dictionary.pop("match")

        for key in format_dictionary:
            clickable = "clickable" in format_dictionary[key]
            prefs = {k: v for k, v in format_dictionary[key].items() if k != "clickable"}
            pattern = re.compile(key)

            # now go through all the rows in the text box
            for row, content in enumerate(current_text.split("\n")):
                matches = [(m.start(), m.end()) for m in re.finditer(pattern, content) if m]

                # now go through all the matches
                for match in matches:
                    start, end = match
                    # simple tag class above to handle working with the tags better
                    tag = Tag(content[start:end],
                              row + 1,
                              start,
                              row + 1,
                              end,
                              prefs=prefs,
                              clickable=clickable)

                    # add them to the tag list
                    self.tag_list.append(tag)

        # now go through the tag list, apply all the tags
        for tag in self.tag_list:
            self.text_box.tag_add(tag.name, tag.start, tag.end)
            self.text_box.tag_config(tag.name, **tag.prefs)
            if tag.clickable:

                if not os.path.isfile(tag.name):
                    if "https://" not in tag.name:
                        url = f"https://{tag.name}"
                    else:
                        url = tag.name
                else:
                    url = tag.name

                self.text_box.tag_bind(tag.name, sequence="<1>",
                                       func=lambda e, url=url: webbrowser.open(url)  # walrus is for binding
                                       )

    def _clear(self):
        self.text_box.delete("1.0", tk.END)

    def _save(self, event):
        with open(self.file_path_variable.get(), 'w') as notes_file:
            notes_file.write(self.text_box.get('1.0', 'end-1c'))

        with open("state.toml", "w") as state_file:
            config.state['last_file']['path'] = self.file_path_variable.get()
            toml.dump(config.state, state_file)

    def run(self):
        self.root.mainloop()
