import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox, PhotoImage
import re
import webbrowser
from tkinter import filedialog as fd
import toml
import config
from menu_framework import FileMenu, AboutMenu, EditMenu, PopupMenu
import pyperclip

class Tag:

    def __init__(self,
                 name,
                 row_1,
                 start,
                 row_2,
                 end,
                 prefs=None,
                 url=None,
                 clickable=0,
                 render_latex=None,
                 image_file=None):
        self.name = name
        self.start = f"{row_1}.{start}"
        self.end = f"{row_2}.{end}"

        self.clickable = clickable
        self.prefs = prefs
        self.render_latex = render_latex
        self.image_file = image_file


class App:
    def __init__(self):
        # set up the main window for the app
        self.root = tk.Tk()
        self.root.title('PatNotes 2.0')
        self.root.geometry('512x512')
        self.root.minsize(512, 256)

        # tk variables
        self.search_bar_variable = tk.StringVar(self.root)
        self.file_path_variable = tk.StringVar(self.root,
                                               value=config.state['last_file']['path'])

        # program variables
        self.tag_list = []

        # top menu bar
        self.menu = tk.Menu(self.root, bg=config.editor_background_color, fg=config.editor_text_color)
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
        self.top_label = tk.Label(self.root,
                                  textvariable=self.file_path_variable,
                                  bg=config.editor_background_color, fg=config.editor_text_color
                                  )
        self.search_bar_label = tk.Label(self.root,
                                         text="Search:",
                                         bg=config.editor_background_color, fg=config.editor_text_color
                                         )

        self.search_bar = tk.Entry(self.root,
                                   bg=config.editor_background_color,
                                   fg=config.editor_text_color,
                                   highlightcolor=config.editor_highlight_color,
                                   insertbackground=config.editor_cursor_color,

                                   )
        self.search_bar_results_label = tk.Label(self.root,
                                                 textvariable=self.search_bar_label,
                                                 bg=config.editor_background_color, fg=config.editor_text_color
                                                 )
        self.text_box = ScrolledText(self.root,
                                     bg=config.editor_background_color,
                                     fg=config.editor_text_color,
                                     highlightcolor=config.editor_highlight_color,
                                     insertbackground=config.editor_cursor_color,
                                     # wrap="none", # turn on our off as desired
                                     tabs=(config.tab,)
                                     )

        self.popup_menu = PopupMenu(self)

        # bind the keyboard controls
        self.search_bar.bind("<KeyRelease>", self._refresh)
        self.text_box.bind("<KeyRelease>", self._refresh)
        self.root.bind("<Escape>", lambda event: self.quit())

        # bind right clicks
        def on_right_click(event):
            try:
                self.popup_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.popup_menu.grab_release()
        self.root.bind("<Button-3>", on_right_click)

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
        print(string_to_paste)
        self.text_box.insert(tk.INSERT, string_to_paste)

    def copy(self):
        pyperclip.copy(self.text_box.selection_get())
        #command = f'echo "{self.text_box.selection_get()[0:-1]}" | xclip -sel c -f'
        #os.system(command)

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
                self.text_box.see(tk.END)

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

        protected = ["multiline", "clickable", 'render_latex', "image_file"]
        for key in format_dictionary:
            clickable = "clickable" in format_dictionary[key]
            render_latex = "render_latex" in format_dictionary[key]
            image_file = "image_file" in format_dictionary[key]

            prefs = {k: v for k, v in format_dictionary[key].items() if k not in protected}
            pattern = re.compile(key)

            # now go through all the rows in the text box for single line
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
                              clickable=clickable,
                              image_file=image_file, render_latex=render_latex)

                    # add them to the tag list
                    self.tag_list.append(tag)

        # multiline stuff is a bit harder... but not crazy
        for key in format_dictionary:
            clickable = "clickable" in format_dictionary[key]
            if "multiline" not in format_dictionary[key]:
                # only work with multiline formats
                continue

            prefs = {k: v for k, v in format_dictionary[key].items()
                     if k not in protected}  # only include preferences that will parse in the tags

            pattern = re.compile(key)
            matches = [(m.start(), m.end()) for m in re.finditer(pattern, current_text) if m]
            for match in matches:
                start, end = match
                match_text = current_text[start: end].split('\n')[0]
                row_1 = current_text[0: start].count("\n") + 1
                rows_covered = current_text[start: end].count("\n")

                start_index = current_text.split("\n")[row_1 - 1].index(match_text)

                tag = Tag(current_text[start:end], row_1, start_index, row_1 + rows_covered, end, prefs=prefs, clickable=clickable)
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

            if tag.render_latex:
                pass

            if tag.image_file:
                self.text_box.tag_bind(tag.name, sequence="<1>",
                                       func=lambda e: webbrowser.open(tag.name[5:-6])
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
