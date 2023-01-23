#!/usr/bin/env python3

# If you're a Windows user trying to get this to work, you have two options:
# The first is to download the official Python package for Windows at https://www.python.org/
# and run this file through that. The second is to use the Windows Subsystem for Linux, like so:
#     C:\> wsl apt install python3
#     C:\> wsl python3 render.py
# If you're from outside Python and worried about setting up virtualenvs and things like that,
# don't be. This script is entirely written with the standard library and requires no dependencies
# except for Python itself.

import argparse
import json
import os
import sys

# command line arguments
# see also: https://docs.python.org/3/library/argparse.html
argparser = argparse.ArgumentParser("render.py", description="Renders single-file versions of these wordlists.")
# if you add a renderer (see below), you should also add it to the choices list here so argparse knows it's real
argparser.add_argument("-o", "--output", choices=["json", "rant"], default="json", help="what type of file to render, defaults to json")
argparser.add_argument("-q", "--quiet", action="store_true", help="suppress progress output")
argparser.add_argument("outfile", action="store", help="output file")

# this will read args passed from the command line
# this actually throws up and exits the script with an error if the args
# are bogus, so beyond this point we can assume all possible argdata
# values are going to be valid
argdata = argparser.parse_args()

quiet = argdata.quiet

def maybe_print(*argl):
    """Prints to stdout, unless -q is passed."""

    if not quiet:
        print(*argl)

def recurse_wordlists(path):
    """Recursive function: reads each wordlist within a given path, calling
    itself on any subdirectories, and returns a dictionary."""

    result = {}
    for item in os.listdir(path):
        # this sets absitem to the calculated "absolute path" of an item
        # this is kind of a naive method, and you may still get relative
        # paths starting explicitly from ".", but that's absolute enough
        # for our purposes
        absitem = "{0}/{1}".format(path, item)

        if os.path.isdir(absitem): 
            # recurse into subdirs
            result[item] = recurse_wordlists(absitem)
        elif item[-4:] == ".txt":
            maybe_print("reading {0}".format(absitem))
            with open(absitem, encoding="utf8") as file:
                result[item[:-4]] = [line.strip() for line in file]
    
    return result

# using the above function, wordlists becomes a dictionary object
# accessing the list at ipsum/lorem.txt is achieved like this:
#     wordlists["ipsum"]["lorem"]   # you get a list

# sys.path[0] should be the directory where this script is located
# if necessary we can add an arg to specify wordlist path
wordlists = recurse_wordlists(sys.path[0])

# setup dictionary and decorator for rendering methods
# these make it so you can just write a function and decorate it with @Render("blah")
# so that the output argument selects it properly
rendering_methods = {}

class Render(object):
    type = ""
    def __init__(self, output):
        # constructor
        self.type = output

    def __call__(self, func):
        # makes this object callable, also defines logic for what the decorator does
        rendering_methods[self.type] = func
        return func # mandatory with decorators
        
# And it works just like this:
@Render("json")
def render_json_file(outpath):
    """JSON renderer. Really just a fancy wrapper for standard library json.dump()."""
    
    outfile = open(outpath, "w", encoding="utf8")
    json.dump(wordlists, outfile)
    outfile.close()

# rant is not in Python stdlib so here's a more complex example of a custom renderer
# functions are not required to be named "render_<format>_file" but it's a good convention
# more about rant itself can be found here: https://rant-lang.org/
@Render("rant")
def render_rant_file(outpath):
    outfile = open(outpath, "w", encoding="utf8")
    outfile.write("<%module = (::)>\n")
    
    def render_list(input):
        return "(: {0} )".format("; ".join(["\"{0}\"".format(inline) for inline in input]))
    
    def recurse_dict(indict, prekey=None):
        for key in indict:
            if prekey:
                fullkey = "{0}/{1}".format(prekey, key)
            else:
                fullkey = key
            
            if type(indict[key]) is list:
                maybe_print("rendering wordlist {0}".format(fullkey))
                outfile.write("<module/{0} = {1}>\n".format(fullkey, render_list(indict[key])))
            elif type(indict[key]) is dict:
                outfile.write("<module/{0} = (::)>\n".format(fullkey))
                recurse_dict(indict[key], fullkey)
    
    recurse_dict(wordlists)

    outfile.write("<module>")
    outfile.close()

# assuming the default "json" for output, the below becomes equivalent to:
# render_json_file(argdata.outfile)
rendering_methods[argdata.output](argdata.outfile)