import tomllib

with open("prefs.toml", "rb") as pref_file:
    prefs = tomllib.load(pref_file)
    print(prefs)

with open('state.toml', "rb") as state_file:
    state = tomllib.load(state_file)
    print(state)