#!/usr/bin/env python

import json

from io import open


json_file = open('colours.json')
data = json.load(json_file)
json_file.close()

string = ''

for colour in data:
	newString = '"' + colour["label"] + '": (' + str(colour["x"]) + ", " + str(colour["y"]) + ", " + str(colour["z"]) + "),\n"
	string += newString

with open("Output.txt", "w", encoding='utf-8') as text_file:
	text_file.write(string)
