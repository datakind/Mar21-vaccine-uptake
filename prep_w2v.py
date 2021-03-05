import os
import shutil
import smart_open
from sys import platform

import gensim


def prepend_line(infile, outfile, line):
    """
    Function use to prepend lines using bash utilities in Linux.
    (source: http://stackoverflow.com/a/10850588/610569)
    """
    with open(infile, 'r', encoding='utf-8') as old:
        with open(outfile, 'w', encoding='utf-8') as new:
            new.write(str(line) + "\n")
            shutil.copyfileobj(old, new)


def prepend_slow(infile, outfile, line):
    """
    Slower way to prepend the line by re-creating the inputfile.
    """
    with open(infile, 'r', encoding='utf-8') as fin:
        with open(outfile, 'w', encoding='utf-8') as fout:
            fout.write(line + "\n")
            for line in fin:
                fout.write(line)


def get_lines(glove_file_name):
    """Return the number of vectors and dimensions in a file in GloVe format."""
    with smart_open.smart_open(glove_file_name, 'r', encoding='utf-8') as f:
        num_lines = sum(1 for line in f)
    with smart_open.smart_open(glove_file_name, 'r', encoding='utf-8') as f:
        num_dims = len(f.readline().split()) - 1
    return num_lines, num_dims


# Input: GloVe Model File
# More models can be downloaded from http://nlp.stanford.edu/projects/glove/
glove_file = "data/00_raw/glove.twitter.27B.200d.txt"

num_lines, dims = get_lines(glove_file)

# Output: Gensim Model text format.
gensim_file = 'data/00_raw/w2v.twitter.27B.200d.txt'
gensim_first_line = "{} {}".format(num_lines, dims)

# Prepends the line.
if platform == "linux" or platform == "linux2":
    prepend_line(glove_file, gensim_file, gensim_first_line)
else:
    prepend_slow(glove_file, gensim_file, gensim_first_line)