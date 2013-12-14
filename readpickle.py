import pickle
import io
import pprint

pkl_file = open('training_data.pkl', 'rb')
outfile = io.open('training_data.arff', 'w', encoding='utf-8')
outfile.write(u"@relation colours\n")
colours = [
  "indigo",
  "gold",
  "yellow",
  "magenta",
  "rosybrown",
  "blue",
  "lightblue",
  "darkorange",
  "lightpurple",
  "seagreen",
  "black",
  "orange",
  "white",
  "midnightblue",
  "red",
  "khaki",
  "teal",
  "salmon",
  "lawngreen",
  "lightgreen",
  "steelblue",
  "maroon",
  "cyan",
  "lightgray",
  "gray",
  "darkgreen",
  "darkgray",
  "purple",
  "saddlebrown",
  "lightpink",
  "green",
  "deeppink"
]

for colour in colours:
  outfile.write(u"@attribute " + colour + u" {yes, no}\n")
outfile.write(u"@data\n")
data1 = pickle.load(pkl_file)
for dictt in data1:
  outfile.write(u','.join("yes" if dictt[colour] > 0 else "no" for colour in colours))
  outfile.write(u"\n")