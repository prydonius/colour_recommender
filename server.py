from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from weka.classifiers import Classifier
# Colour classiier
from colorclassifier import Classifier as ColorClassifier
import io
import operator
import pickle
from subprocess import call
import os
import ast
app = Flask(__name__)

images = {}
PICKLED=True

# To preserve order
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

@app.route("/")
def index():
  colours = ColorClassifier().getColours()
  return render_template('index.html', colours=colours)

@app.route("/multipredict")
def multipredict():
  global colours
  # The users current palette
  palette = dict.fromkeys(colours, 0)
  # palette["white"] = 1
  # palette["black"] = 1
  # palette["salmon"] = 1
  # /predict?colour[]=blue&colour[]=red etc.
  palette_list = request.args.getlist("colour[]")
  for colour in palette_list:
    palette[colour] = 1
  predict_list = []
  num_labels = len(colours) - len(palette_list)
  # Creating training file
  outfile = io.open("training_data.arff", 'w')
  outfile.write(u"@relation 'colours: -C " + str(num_labels) + u"'\n")
  global images
  for colour in colours:
    # Colour is in the palette, we don't want it to be a target attribute
    if colour in palette_list:
      continue
    predict_list.append(colour)
  for colour in predict_list:
    outfile.write(u"@attribute " + colour + u" {0,1}\n")
  for colour in palette_list:
    outfile.write(u"@attribute " + colour + u" {0,1}\n")
  outfile.write(u"@data\n")
  for image in images:
    outfile.write(u','.join("1" if image[c] > 0 else "0" for c in predict_list))
    outfile.write(u",")
    outfile.write(u','.join("1" if image[c] > 0 else "0" for c in palette_list))
    outfile.write(u"\n")
  outfile.close()
  # Create query file
  outfile = io.open("query.arff", 'w')
  outfile.write(u"@relation 'colours: -C " + str(num_labels) + u"'\n")
  for colour in predict_list:
    outfile.write(u"@attribute " + colour + u" {0,1}\n")
  for colour in palette_list:
    outfile.write(u"@attribute " + colour + u" {0,1}\n")
  outfile.write(u"@data\n")
  outfile.write(u','.join("0" for c in predict_list))
  outfile.write(u",")
  outfile.write(u','.join("1" for c in palette_list))
  outfile.write(u"\n")
  outfile.close()
  call([
    "java",
    "-cp", os.environ['MEKA_PATH'],
    "weka.classifiers.multilabel.BR",
    "-t", "training_data.arff",
    "-T", "query.arff",
    "-W", "weka.classifiers.lazy.IBk",
    "-f", "MEKA_OUT"
  ])
  outfile = os.popen("tail -1 " + "MEKA_OUT").readlines()[0]
  probs = ast.literal_eval(outfile.split(":")[1].split("\n")[0])
  map(float, probs)
  j = 0
  predictions = {}
  for prob in probs:
    predictions[predict_list[j]] = prob
    j += 1
  predictions_s = sorted(predictions.iteritems(), key=operator.itemgetter(1), reverse=True)
  print predictions_s
  values = ColorClassifier().getColours()
  top5 = []
  k = 0
  for pred in predictions_s:
    top5.append(dict(name=pred[0], colour=str(values[pred[0]]), probability=pred[1]))
    k += 1
    if k > 4:
      break
  return jsonify(predictions=top5)

if __name__ == "__main__":
  pkl_file = open('training_data.pkl', 'rb')
  images = pickle.load(pkl_file)
  pkl_file.close()
  print("Pickled training data loaded")
  app.run()
