import tomllib
import tkinter as tk
import tkinter.font as tkfont

with open("prefs.toml", "rb") as pref_file:
    prefs = tomllib.load(pref_file)
    print(prefs)

with open('state.toml', "rb") as state_file:
    state = tomllib.load(state_file)
    print(state)

# editor config
editor_background_color = "black"
editor_text_color = "white"
editor_cursor_color = "white"
editor_highlight_color = "pink"

# for the unstoppable tabs/spaces debate
change_me_if_you_want_different_spacing = space = " "
root = tk.Tk()
text = tk.Text(root)

font = tkfont.Font(font=text['font'])
tab = font.measure(3 * space)
root.destroy()
del root
del text
del font
