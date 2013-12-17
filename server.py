from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from weka.classifiers import Classifier
# Colour classiier
from colorclassifier import Classifier as ColorClassifier
import io
import operator
import sys
app = Flask(__name__)

models = {}
PICKLED=False

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
  classifier = "Knn" if sys.argv[1] == "5000" else "Bayes"
  return render_template('index.html', colours=colours, classifier=classifier)

@app.route("/test")
def test():
  print request.args.getlist("yourcolours")
  return "hello"


@app.route("/predict")
def predict():
  global colours
  yourcolours = dict.fromkeys(colours, 0)
  # /predict?colour=blue&colour=red etc.
  requestedcolours = request.args.getlist("colour[]")
  for colour in requestedcolours:
    yourcolours[colour] = 1
  outfile = io.open("query.arff", 'w', encoding='utf-8')
  outfile.write(u"@relation colours\n")
  for colour in colours:
    outfile.write(u"@attribute " + colour + u" {yes, no}\n")
  outfile.write(u"@data\n")
  outfile.write(u','.join("yes" if yourcolours[colour] > 0 else "no" for colour in colours))
  outfile.close()
  global models
  j = 0
  predictions = {}
  for colour in colours:
    j += 1
    # Colour is already in the palette, skip prediction
    if yourcolours[colour] == 1:
      continue
    # run a prediction for this colour
    prediction = list(models[colour].predict('query.arff', False, False, None, j))[0]
    predictions[colour] = (prediction[2] if prediction[1] == "yes" else 1 - prediction[2])
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
  print("Training models, this may take a while")
  j = 0
  for colour in colours:
    j += 1
    if PICKLED:
      models[colour] = Classifier.load('models/' + colour + '.pkl')
    else:
      models[colour] = Classifier(name='weka.classifiers.lazy.IBk', ckargs={'-K':1,'-c':j})
      models[colour].train('2500set.arff')
      models[colour].save('models/' + colour + '.pkl')
  print("Trained - Ready")
  app.run(port=sys.argv[1])
  print("Server started")
