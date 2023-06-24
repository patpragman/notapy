import toml

d = {"#": {
    "a": 1,
    "b": 2,
    "c": "..."
},
        "##": "test 2"}

with open('test.toml', 'w') as t:
    toml.dump(d, t)
