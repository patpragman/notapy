import tkinter as tk
import webbrowser


class FileMenu(tk.Menu):

    def __init__(self,
                 parent,
                 app,
                 new_command=lambda: print('New Clicked from Menu'),
                 load_command=lambda: print('Load Clicked from Menu'),
                 export_command=lambda: print('Export clicked from Menu'),
                 quit_command=lambda: print('Quit Clicked from Menu'),
                 prefs_command=lambda:print('Prefs Clicked from Menu')):
        super().__init__()

        self.parent = parent
        self.app = app

        self.add_command(label="New", command=new_command)
        self.add_command(label="Load", command=load_command)
        self.add_command(label="Export", command=export_command)
        self.add_command(label="Quit", command=quit_command)


class EditMenu(tk.Menu):

    def __init__(self,
                 parent,
                 app,
                 cut_command=lambda e: print('Cut Clicked from Menu'),
                 copy_command=lambda e: print('Copy Clicked from Menu'),
                 paste_command=lambda e: print('Paste Clicked from Menu'),
                 select_all_command=lambda e: print('Select All from Menu'),
                 cut_key="<Control-x>",
                 copy_key="<Control-c>",
                 paste_key="<Control-v>",
                 select_all_key="<Control-a>"
                 ):
        super().__init__()

        self.parent = parent
        self.app = app

        self.add_command(label="Select All", command=select_all_command)
        self.add_command(label="Cut", command=cut_command)
        self.add_command(label="Copy", command=copy_command)
        self.add_command(label="Paste", command=paste_command)

        self.app.root.bind(select_all_key, select_all_command)
        self.app.root.bind(cut_key, cut_command)
        self.app.root.bind(copy_key, copy_command)
        self.app.root.bind(paste_key, paste_command)

class AboutMenu(tk.Menu):

    def __init__(self,
                 parent,
                 app,
                 about_command=lambda: webbrowser.open("https://github.com/patpragman/notapy"),
                 help_command=lambda: webbrowser.open("https://www.pragman.io"),
                 ):
        super().__init__()

        self.parent = parent
        self.app = app

        self.add_command(label="Project Github", command=about_command)
        self.add_command(label="About Me", command=help_command)


class PopupMenu(tk.Menu):
    # todo: set up popup window here
    def __init__(self,
                 parent,
                 commands=((lambda: print(f'hello world'), f"Function {i}") for i in range(0, 5))
                 ):
        super().__init__()

        self.parent = parent

        for command, label in commands:
            self.add_command(label=label, command=command)

