import pickle
import io
import pprint
from colorclassifier import Classifier

pkl_file = open('training_data.pkl', 'rb')
outfile = io.open('training_data.arff', 'w', encoding='utf-8')
outfile.write(u"@relation colours\n")
colorclassifier = Classifier()
colours = dict.fromkeys(colorclassifier.getColours().keys(), 0)

for colour in colours:
  colour = colour.replace(' ','')
  colour = colour.replace("'",'')
  outfile.write(u"@attribute " + colour + u" {yes, no}\n")
outfile.write(u"@data\n")
data1 = pickle.load(pkl_file)
for dictt in data1:
  outfile.write(u','.join("yes" if dictt[colour] > 0 else "no" for colour in colours))
  outfile.write(u"\n")