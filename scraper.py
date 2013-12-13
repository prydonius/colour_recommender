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

# Other Libraries
from collections import namedtuple
import cStringIO
import io
import requests
import shutil

palette = namedtuple('Palette', ['dominant', 'others'])

# Set the number of colours we want
COLOUR_PALETTE_SIZE = 5
# Dribbble settings
DRIBBBLE_NUMBER_IMAGES = 50
DRIBBLE_STREAM = "popular"
FILENAME = "2500set.arff"

def getPalette(image):
	array = scipy.misc.fromimage(image)
	shape = array.shape
	array = array.reshape(scipy.product(shape[:2]), shape[2])
	# Use K-Means to get the n most used colours
	colours, dist = scipy.cluster.vq.kmeans(array, COLOUR_PALETTE_SIZE)

	# Get the most dominant colour from this
	vecs, dist = scipy.cluster.vq.vq(array, colours)
	counts, bins = scipy.histogram(vecs, len(colours))
	index_max = scipy.argmax(counts)

	# Remove the dominant from the colours
	colours = colours.tolist()
	if len(colours) == COLOUR_PALETTE_SIZE:
		# dominant = colours[index_max]
		# del colours[index_max]

		# Return the palette
		# p = palette(dominant, colours)
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
	# dominant = Image.new(image.mode, (20, 20), "white")
	# drawD = ImageDraw.Draw(dominant)
	# drawD.rectangle([(0, 0), (20, 20)], fill = tuple(palette[0]))

	# Show the palettes and original image
	# dominant.show()
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
	outfile.write(u"@relation colours\n")
	colours = {
		"blacks": 0,
		"whites": 0,
		"grays": 0,
		"reds": 0,
		"yellows": 0,
		"greens": 0,
		"cyans": 0,
		"blues": 0,
		"magentas": 0
	}
	for colour in colours:
		outfile.write(u"@attribute " + colour + u" {yes, no}\n")
	outfile.write(u"@data\n")
	for i in range(0, DRIBBBLE_NUMBER_IMAGES):
		# 50 is the maximum per page
		resp = drib.shots('popular', per_page=50, page=page)
		for shot in resp["shots"]:
			# Get the image and open it
			response = requests.get(shot["image_teaser_url"], stream=True)
			#response = requests.get(shot["image_teaser_url"])
			raw_image = cStringIO.StringIO(response.content)
			img = Image.open(raw_image).convert('RGB')
			palette = getPalette(img)
			print palette
			user_id = shot["id"]
			colours = {
				"blacks": 0,
				"whites": 0,
				"grays": 0,
				"reds": 0,
				"yellows": 0,
				"greens": 0,
				"cyans": 0,
				"blues": 0,
				"magentas": 0
			}
			if palette is not None:
				drawPalette(palette, img)
				palette = convertRGB2HSV(palette)
				# print palette
				palettes.append(palette)
				for colour in palette:
					# Lightness
					if colour[1] < 0.2:
						colours["blacks"] += 1
					elif colour[1] > 0.8:
						colours["whites"] += 1
					# Saturation
					elif colour[2] < 0.25:
						colours["grays"] += 1
					# Hues
					elif colour[0] < 30 / float(360):
						colours["reds"] += 1
					elif colour[0] < 90 / float(360):
						colours["yellows"] += 1
					elif colour[0] < 150 / float(360):
						colours["greens"] += 1
					elif colour[0] < 210 / float(360):
						colours["cyans"] += 1
						print colour[0]
					elif colour[0] < 270 / float(360):
						colours["blues"] += 1
					elif colour[0] < 330 / float(360):
						colours["magentas"] += 1
					else:
						colours["reds"] += 1
				print(colours)
				outfile.write(u','.join("yes" if colours[colour] > 0 else "no" for colour in colours))
				outfile.write(u"\n")
				raw_input("Press Enter to continue...")
		count += 50
		if count >= DRIBBBLE_NUMBER_IMAGES:
			break
		page += 1

if __name__ == "__main__":
	palette = fetchShots()
