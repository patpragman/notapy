# Hi!  Welcome to NotaPy
## Pat Pragman's extremely simple note tool

### Install

clone this repository:  https://github.com/patpragman/notapy.git

www.google.com

run the following code:


```
# make a virtual environment:
python -m venv venv

# turn it on
source venv/bin/activate

# install the requirements (which is really only the toml library)
pip install -r requirements.txt

# run with

python main.py

```


### Features

* Customizable Syntax Highlighting
* Clickable Links for example github.com/patpragman
* fully searchable with regex

### Current Bugs

Sorry, cut and paste menus are still behaving strangely, like this was like 3 hours work today while my kids were playing.
I will fix it.

You can sometimes get into situations where you get regex errors, they aren't really handled but the command line may
get cluttered up.


### Future Plans

* LaTex Support - I would like real time latex rendering
* LLM support where you could highlight text, right click on it, then have chatgpt improve the writing
* some popup cheat sheets for regex stuff
* darkmode
* export to pdf?
* image embedding?


