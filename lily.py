#!/usr/bin/python

import os
import re
import sys
from optparse import OptionParser
from subprocess import DEVNULL, Popen

YAMAHASF2 = '/home/sebastien/.piano/Yamaha C5 Grand-v2.3.sf2'

HEADER = """
\\include "italiano.ly"
\\version "2.22.0"
\\score {
  \\relative do {
"""

def get_footer(tempo):
    return (
        "  }\n"
        "  \\layout { }\n"
        "  \\midi {\n"
        f"    \\tempo 4 = {tempo}\n"
        "  }\n"
        "}\n"
    )

CONVERT = {
    'dob': 'do',
    'dod': 're',
    'do': 'dod',
    'reb': 're',
    'red': 'mi',
    're': 'red',
    'mib': 'mi',
    'mid': 'fad',
    'mi': 'fa',
    'fab': 'fa',
    'fad': 'sol',
    'fa': 'fad',
    'solb': 'sol',
    'sold': 'la',
    'sol': 'sold',
    'lab': 'la',
    'lad': 'si',
    'la': 'lad',
    'sib': 'si',
    'sid': 'dod',
    'si': 'do',
}
BTOCKEN = '##iuaibiiii##'
ETOCKEN = '##rsmnrsnmr##'

def entocken(s):
    return BTOCKEN + s + ETOCKEN


def increase(s):
    s = re.sub('(dob|dod|do|reb|red|re|mib|mid|mi|fab|fad|fa|solb|sold|sol|lab|lad|la|sib|sid|si)', entocken('\\1'), s)

    for initial, final in CONVERT.items():
        s = re.sub(entocken(initial), final, s)
    return s


def generate_pyramid(string, level):
    if level == 0:
        return string + '\n'
    else:
        return string + '\n' + generate_pyramid(increase(string), level - 1) + string + '\n'


def generate_notes(string, level):
    return string + '\n' + generate_pyramid(increase(string), level - 1)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="write to FILE", metavar="FILE", default="lily")
    parser.add_option('-l', "--length", action="store", type=int, default=10)
    parser.add_option('-t', "--tempo", action="store", type=int, default=60)
    parser.add_option('-m', "--mplayer", action="store_true", dest="mplayer")

    (options, args) = parser.parse_args()

    if len(args) < 1:
        print("You must provide a string")
        sys.exit(1)

    string = args[0]
    if len(args) > 1:
        filename = args[1]
    else:
        filename = options.filename
    lyfile = filename + ".ly"

    print("Create lilypond file…", end=" ")
    with open(lyfile, "w") as file:
        file.write(HEADER)
        file.write(generate_notes(string, options.length))
        file.write(get_footer(options.tempo))
        file.close()
    print("ok")

    print("Run lilypond…", end=" ")
    proc = Popen(["lilypond", lyfile], stdout=DEVNULL, stderr=DEVNULL)
    proc.wait()
    print("ok")

    print("Run convert midi to flac…", end=" ")
    proc = Popen(["fluidsynth", "-F", filename + ".flac", YAMAHASF2, filename + ".midi"], stdout=DEVNULL, stderr=DEVNULL)
    proc.wait()
    print("ok")

    print("Cleaning…", end=" ")
    os.remove(filename + ".midi")
    print("ok")

    print("Generated files:", lyfile, filename + ".pdf", filename + ".flac")

    if options.mplayer:
        print("Play it with mlayer!")
        try:
            proc = Popen(["mplayer", filename + ".flac"], stdout=DEVNULL, stderr=DEVNULL)
            proc.wait()
        except KeyboardInterrupt:
            pass

