#!/usr/bin/python
import re
from itertools import izip_longest
import argparse 
""" 
    Iterate over two gcode files and interleave them together, layer by layer.
    Assumes that the two files have been sliced to the same layer height.
    Puts both into memory, may be problematic for very large gcode files.
    A cleaner solution may involve coroutines and/or generator functions.
    Written by Joseph Lenox
""" 

parser = argparse.ArgumentParser(description='Combine 2 gcode files from Slic3r, alternating every other layer')
parser.add_argument('files', metavar='F', type=str, nargs=2,
                    help='gcode input')
parser.add_argument('--output', type=str, default="output-merged.gcode", help='merged output name')
parser.add_argument('--regex', type=str, default="; move to next layer \(([0-9]*)\)", help="Regular expression to parse the layer from. It must include the layer number as the first submatch. Default matches Slic3r's verbose output.")

args = parser.parse_args()
file_1 = args.files[0]
file_2 = args.files[1]
layers_1 = {}
layers_2 = {}

layer_1 = -1
layer_2 = -1
layers_1[-1] = []
layers_2[-1] = []
nextlayer = re.compile(args.regex)
for line_from_file_1, line_from_file_2 in izip_longest(open(file_1), open(file_2)):
    if line_from_file_1 is not None:
        if re.search(nextlayer, line_from_file_1) is not None:
            layer_1 = int(re.search(nextlayer, line_from_file_1).group(1))
            layers_1[layer_1] = []
        layers_1[layer_1].append(line_from_file_1)

    if line_from_file_2 is not None:
        if re.search(nextlayer, line_from_file_2) is not None:
            layer_2 = int(re.search(nextlayer, line_from_file_2).group(1))
            layers_2[layer_2] = []
        layers_2[layer_2].append(line_from_file_2)

max_layer = max(layer_2, layer_1)
with open(args.output, 'wb') as output:
    for x in range(-1, max_layer+1):
        if x % 2 is 0 or len(layers_2) < x:
            for l in layers_1[x]:
                output.write(l)
        else:
            for l in layers_2[x]:
                output.write(l)
