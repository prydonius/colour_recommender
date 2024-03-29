#!/usr/bin/env python

# Imaging library
from PIL import Image, ImageDraw
import colorsys

# Scientific clustering library
import scipy
import scipy.misc
import scipy.cluster

# Dribbble API
import dribbble as drib

# Colour classiier
from colorclassifier import Classifier

# Other Libraries
from collections import namedtuple
import cStringIO
import io
import requests
import shutil
import pickle
import copy

# Set the number of colours we want
COLOUR_PALETTE_SIZE = 5
# Dribbble settings
DRIBBBLE_NUMBER_IMAGES = 10
DRIBBLE_STREAM = "popular"
FILENAME = "2500set_newColours.arff"

def getPalette(image):
	array = scipy.misc.fromimage(image)
	shape = array.shape
	array = array.reshape(scipy.product(shape[:2]), shape[2])
	# Use K-Means to get the n most used colours
	colours, dist = scipy.cluster.vq.kmeans(array, COLOUR_PALETTE_SIZE)

	colours = colours.tolist()
	if len(colours) == COLOUR_PALETTE_SIZE:
		return colours
	else:
		return None

def drawPalette(palette, image):
	# Draw out the palette
	paletteImage = Image.new(image.mode, (20, 20*COLOUR_PALETTE_SIZE), "white")
	draw = ImageDraw.Draw(paletteImage)
	i=0
	for colour in palette:
		draw.rectangle([(0, i*20),((i+1)*20, (i+1)*20)], fill=tuple(colour))
		i += 1

	# Draw out the dominant colour
	dominant = Image.new(image.mode, (20, 20), "white")
	drawD = ImageDraw.Draw(dominant)
	drawD.rectangle([(0, 0), (20, 20)], fill = tuple(palette[0]))

	# Show the palettes and original image
	dominant.show()
	paletteImage.show()
	image.show()

def convertRGB2HSV(palette):
	HSVPalette = []
	for colour in palette:
		ct = tuple(colour)
		HSVColour = colorsys.rgb_to_hls(ct[0] / float(256), ct[1] / float(256), ct[2] / float(256))
		HSVPalette.append(HSVColour)

	return HSVPalette

def view_colour(client, user_id, item_id):
	client.identify(user_id)
	client.record_action_on_item("view", item_id)

def fetchShots():
	count = 0
	page = 0
	outfile = io.open(FILENAME, 'w', encoding='utf-8')
	palettes = []
	# Array of each image data to be pickled
	training_data = []
	outfile.write(u"@relation colours\n")
	colorclassifier = Classifier()
	colours = dict.fromkeys(colorclassifier.getColours().keys(), 0)

	for colour in colours:
		colour = colour.replace(' ','')
		colour = colour.replace("'",'')
		outfile.write(u"@attribute " + colour + " {yes, no}\n")
	outfile.write(u"@data\n")
	for i in range(0, DRIBBBLE_NUMBER_IMAGES):
		# 50 is the maximum per page
		resp = drib.shots('popular', per_page=10, page=page)
		for shot in resp["shots"]:
			# Get the image and open it
			response = requests.get(shot["image_teaser_url"], stream=True)
			#response = requests.get(shot["image_teaser_url"])
			raw_image = cStringIO.StringIO(response.content)
			img = Image.open(raw_image).convert('RGB')
			palette = getPalette(img)
			print palette
			user_id = shot["id"]

			# Reset the colours
			for colour in colours:
				colours[colour] = 0

			if palette is not None:
				drawPalette(palette, img)
				palettes.append(palette)
				j = 0
				for colour in palette:
					classifiedColour = colorclassifier.getColourName(colour)
					print("colour " + str(j) + ": " + classifiedColour + " ")
					colours[classifiedColour] += 1
					j += 1
				# print(colours)
				training_data.append(copy.copy(colours))
				outfile.write(u','.join("yes" if colours[colour] > 0 else "no" for colour in colours))
				outfile.write(u"\n")
				raw_input("Press Enter to continue...")
		count += 50
		if count >= DRIBBBLE_NUMBER_IMAGES:
			break
		page += 1
	td_file = io.open("training_data.pkl", 'wb')
	pickle.dump(training_data, td_file)
	td_file.close()

if __name__ == "__main__":
	palette = fetchShots()
